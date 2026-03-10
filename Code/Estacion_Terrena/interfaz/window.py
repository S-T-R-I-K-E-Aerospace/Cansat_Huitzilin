import sys
import os
import csv
import glob
import re
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from ui.panels import HeaderPanel, TelemetryPanel, ControlPanel, FooterPanel, GraphPanel
from ui.widgets import MetalPanel, CameraView, LogConsole
from ui import styles
from core.serial_reader import SerialReader
from core.simulator import TelemetrySimulator

def get_base_dir():
    """Retorna la carpeta base: donde está el .exe/_internal si está empaquetado, o donde está el .py si no."""
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        base = os.path.dirname(sys.executable)
        if os.path.isdir(os.path.join(base, '_internal')):
             return os.path.join(base, '_internal')
        return base
    return os.path.dirname(os.path.abspath(__file__))

def get_user_data_dir():
    """Retorna carpeta para datos del usuario (received_images, etc.).
    Como script: carpeta del proyecto. Como .exe: Documents/STRIKE_Aerospace."""
    if getattr(sys, 'frozen', False):
        docs = os.path.join(os.path.expanduser('~'), 'Documents', 'STRIKE_Aerospace')
        os.makedirs(docs, exist_ok=True)
        return docs
    return os.path.dirname(os.path.abspath(__file__))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S.T.R.I.K.E Aerospace - Mission Control v1.0.1")
        self.resize(1400, 900)
        self.setWindowIcon(QIcon(os.path.join(get_base_dir(), "assets", "Logo_de_la_UAM-A.png")))
        self.setStyleSheet(styles.MAIN_WINDOW_STYLE)

        self.data_ticks = 0.0  # Contador para el eje X de la gráfica

        # --- CSV Flight Logger ---
        self._csv_file = None
        self._csv_writer = None
        self._csv_path = None
        self.received_files_dir = os.path.join(get_user_data_dir(), "received_files")
        try:
            os.makedirs(self.received_files_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorio received_files: {e}")

        # --- Serial ---
        self.serial_reader = SerialReader(baudrate=115200)
        self.serial_reader.data_updated.connect(self.on_telemetry_updated)
        self.serial_reader.raw_data_received.connect(self.on_raw_data)
        self.serial_reader.connection_status.connect(self.update_header_status)

        # --- Simulador ---
        self.simulator = TelemetrySimulator()
        self.simulator.data_updated.connect(self.on_telemetry_updated)
        self.simulator.raw_data_received.connect(self.on_raw_data)

        self.setup_ui()

        self.refresh_port_list()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.header = HeaderPanel()
        main_layout.addWidget(self.header)

        body_layout = QHBoxLayout()

        # Izquierda
        self.telemetry = TelemetryPanel()
        body_layout.addWidget(self.telemetry)

        # Centro (Gráfica Real)
        self.graph_panel = GraphPanel()
        body_layout.addWidget(self.graph_panel, stretch=1)

        # Derecha
        right_container = QWidget()
        right_container.setFixedWidth(450)
        right_layout = QVBoxLayout(right_container)

        cam_panel = MetalPanel("CANSAT CAMERA MONITOR")
        self.camera_view = CameraView("Estereocámara del Cansat")
        cam_panel.get_content_layout().addWidget(self.camera_view)
        self.camera_view.log_message.connect(self.on_system_log)

        # Monitorear carpeta de imágenes recibidas (polling cada 2s)
        self.images_dir = os.path.join(get_user_data_dir(), "received_images")
        try:
            os.makedirs(self.images_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorio de imágenes: {e}")
            
        self._last_image_mtime = 0
        self._last_image_path = None
        self._image_poll_timer = QTimer()
        self._image_poll_timer.timeout.connect(self._poll_images)
        # Timer se inicia pero primer poll se hace después de crear log_console
        self._image_poll_timer.start(2000)

        self.control = ControlPanel()
        self.control.connection_toggled.connect(self.handle_connection_toggle)
        self.control.refresh_requested.connect(self.refresh_port_list)
        self.control.simulate_toggled.connect(self.handle_simulate_toggle)
        self.control.clear_requested.connect(self.clear_all_data)

        right_layout.addWidget(cam_panel)
        right_layout.addWidget(self.control)
        
        # -- Log Console Panel (RAW SERIAL)
        log_panel = MetalPanel("RAW SERIAL LOGS")
        self.log_console = LogConsole()
        log_panel.get_content_layout().addWidget(self.log_console)
        # Que crezca para llenar el espacio libre verticalmente
        right_layout.addWidget(log_panel, stretch=1)

        body_layout.addWidget(right_container)
        main_layout.addLayout(body_layout, stretch=1)

        # Primera revisión de imágenes (telemetry.sys_log ya existe)
        self._poll_images()

        self.footer = FooterPanel()
        main_layout.addWidget(self.footer)

    def refresh_port_list(self):
        ports = SerialReader.get_available_ports()
        self.control.update_ports(ports)

    # ── CSV Flight Logger helpers ──────────────────────────────────
    def _next_flight_number(self):
        """Busca el siguiente número de vuelo disponible (0001-9999)."""
        existing = glob.glob(os.path.join(self.received_files_dir, "Vuelo_????.csv"))
        used = set()
        for path in existing:
            m = re.search(r'Vuelo_(\d{4})\.csv$', os.path.basename(path))
            if m:
                used.add(int(m.group(1)))
        for n in range(1, 10000):
            if n not in used:
                return n
        return None  # Límite alcanzado

    def _start_csv_recording(self):
        """Abre un nuevo archivo CSV para registrar datos del vuelo."""
        num = self._next_flight_number()
        if num is None:
            self.telemetry.sys_log.append_log("[CSV] ERROR: Límite de 9999 vuelos alcanzado")
            return
        filename = f"Vuelo_{num:04d}.csv"
        self._csv_path = os.path.join(self.received_files_dir, filename)
        try:
            self._csv_file = open(self._csv_path, 'w', newline='', encoding='utf-8')
            self._csv_writer = csv.writer(self._csv_file)
            self._csv_writer.writerow([
                'time_s', 'altitude', 'velocity', 'acceleration',
                'temperature', 'pressure', 'battery', 'heading',
                'deployed', 'latitude', 'longitude'
            ])
            self.telemetry.sys_log.append_log(f"[CSV] Grabando: {filename}")
        except Exception as e:
            self.telemetry.sys_log.append_log(f"[CSV] ERROR abriendo archivo: {e}")
            self._csv_file = None
            self._csv_writer = None

    def _stop_csv_recording(self):
        """Cierra el archivo CSV actual."""
        if self._csv_file:
            try:
                self._csv_file.close()
                self.telemetry.sys_log.append_log(f"[CSV] Guardado: {os.path.basename(self._csv_path)}")
            except Exception as e:
                self.telemetry.sys_log.append_log(f"[CSV] ERROR cerrando: {e}")
            self._csv_file = None
            self._csv_writer = None
            self._csv_path = None

    def _write_csv_row(self, data):
        """Escribe una fila de telemetría al CSV."""
        if self._csv_writer:
            try:
                self._csv_writer.writerow([
                    f"{self.data_ticks:.1f}",
                    f"{data['altitude']:.2f}",
                    f"{data['velocity']:.2f}",
                    f"{data['acceleration']:.2f}",
                    f"{data['temperature']:.2f}",
                    f"{data['pressure']:.2f}",
                    f"{data['battery']:.1f}",
                    f"{data.get('heading', 0.0):.1f}",
                    int(data.get('deployed', False)),
                    f"{data.get('latitude', 0.0):.6f}",
                    f"{data.get('longitude', 0.0):.6f}",
                ])
                self._csv_file.flush()
            except Exception:
                pass

    # ── Handlers de conexión / simulación ─────────────────────────
    def handle_connection_toggle(self, is_active, port_name):
        if is_active:
            self.header.update_status("CONNECTING...", "#ffb74d")
            self.serial_reader.port = port_name
            self.serial_reader.start()
            self._start_csv_recording()
            self.telemetry.sys_log.append_log(f"[SYS] Conectando a {port_name}...")
        else:
            self.serial_reader.stop()
            self._stop_csv_recording()
            self.telemetry.sys_log.append_log("[SYS] Desconectado")

    def handle_simulate_toggle(self, is_active):
        if is_active:
            self.header.update_status("SIMULATING", "#e3b341")
            self.simulator.start(update_interval_ms=100)
            self._start_csv_recording()
            self.telemetry.sys_log.append_log("[SYS] Simulación iniciada")
        else:
            self.simulator.stop()
            self._stop_csv_recording()
            self.header.update_status("DISCONNECTED", "#ff5252")
            self.telemetry.sys_log.append_log("[SYS] Simulación detenida")

    def clear_all_data(self):
        self.data_ticks = 0.0
        self.telemetry.clear_data()
        self.graph_panel.clear_graph()
        self.footer.update_battery(0.0)
        self.footer.update_heading(0.0)
        self.footer.update_gps(0.0, 0.0)
        self.camera_view.clear_image()
        self.log_console.clear_logs()
        self.telemetry.sys_log.clear_logs()
        # Resetear tracking para que se recargue la imagen si se vuelve a añadir
        self._last_image_mtime = 0
        self._last_image_path = None

    def update_header_status(self, status_text, color):
        self.header.update_status(status_text, color)
        self.telemetry.sys_log.append_log(f"[SYS] {status_text}")
        if status_text == "PORT ERROR" and self.control.is_connected:
            self.control.toggle()

    def on_telemetry_updated(self, data):
        self.data_ticks += 0.1  # Avanzamos el tiempo (asumiendo 100ms por dato)

        # Panel izquierdo: telemetría + presión
        self.telemetry.update_data(data['altitude'], data['velocity'], data['acceleration'], data['temperature'], data['pressure'])
        self.telemetry.update_pressure(data['pressure'])

        # Footer: batería + heading
        self.footer.update_battery(data['battery'])
        heading = data.get('heading', 0.0)
        self.footer.update_heading(heading)
        self.footer.update_gps(data.get('latitude', 0.0), data.get('longitude', 0.0))

        # Gráfica central
        deployed = data.get('deployed', False)
        self.graph_panel.update_graph(self.data_ticks, data['altitude'], deployed)

        # Guardar en CSV
        self._write_csv_row(data)

    def on_raw_data(self, raw_str):
        self.log_console.append_log(raw_str)

    def on_system_log(self, msg):
        self.telemetry.sys_log.append_log(msg)

    def _poll_images(self):
        """Revisa la carpeta de imágenes y carga la más reciente si es nueva."""
        valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        try:
            files = os.listdir(self.images_dir)
            images = [
                os.path.join(self.images_dir, f) for f in files
                if f.lower().endswith(valid_exts)
            ]
            if not images:
                return
            newest = max(images, key=os.path.getmtime)
            mtime = os.path.getmtime(newest)
            # Solo cargar si es una imagen nueva, diferente, o modificada
            if newest != self._last_image_path or mtime != self._last_image_mtime:
                self.telemetry.sys_log.append_log(f"[CAM] Nueva imagen: {os.path.basename(newest)}")
                self._last_image_mtime = mtime
                self._last_image_path = newest
                self.camera_view.update_image(newest)
        except Exception as e:
            self.telemetry.sys_log.append_log(f"[CAM] Error: {e}")
