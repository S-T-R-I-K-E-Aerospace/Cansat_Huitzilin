import sys
import math
import os
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QComboBox, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QPoint
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QPolygon, QFont
import pyqtgraph as pg
import math
from ui.widgets import DataDisplay, MetalPanel, CameraView
from ui import styles

def _get_base_dir():
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        base = os.path.dirname(sys.executable)
        if os.path.isdir(os.path.join(base, '_internal')):
             return os.path.join(base, '_internal')
        return base
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class HeaderPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-bottom: 1px solid #21262d;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # --- LOGO DEL EQUIPO ---
        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("background: transparent; border: none;")
        
        logo_path = os.path.join(_get_base_dir(), "assets", "LogoSTRIKE300.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            # Escalamos a 70px para que ocupe muy bien el espacio vertical de 90px
            scaled_pixmap = pixmap.scaledToHeight(90, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            self.logo_label.setText("⚠️ LOGO NO ENCONTRADO")
            self.logo_label.setStyleSheet("color: #ff5252; font-weight: bold; background: transparent; border: none;")
            
        layout.addWidget(self.logo_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        
        layout.addStretch()
        
        # Misión
        mission_label = QLabel("MISSION: CANSAT WORLD CUP 2026")
        mission_label.setStyleSheet("background: transparent; color: #8b949e; font-size: 15px; font-weight: bold; padding: 0px; border: none; letter-spacing: 2px;")
        layout.addWidget(mission_label)
        
        layout.addStretch() 
        
        # Status
        status_container = QHBoxLayout()
        status_label = QLabel("STATUS:")
        status_label.setStyleSheet("background: transparent; color: #8b949e; font-size: 14px; font-weight: bold; padding: 0px; border: none; letter-spacing: 1px;")
        
        self.status_value = QLabel("DISCONNECTED")
        self.status_value.setStyleSheet("background: transparent; color: #ff7b72; font-size: 16px; font-weight: bold; padding: 0px 5px; border: none; letter-spacing: 2px;")

        # Efecto neón en el texto
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(20)
        self.glow_effect.setColor(QColor("#ff7b72"))
        self.glow_effect.setOffset(0, 0)
        self.status_value.setGraphicsEffect(self.glow_effect)

        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("background: transparent; color: #ff7b72; font-size: 20px; padding: 0px; border: none;")

        # Efecto neón en el indicador
        self.glow_indicator = QGraphicsDropShadowEffect()
        self.glow_indicator.setBlurRadius(25)
        self.glow_indicator.setColor(QColor("#ff7b72"))
        self.glow_indicator.setOffset(0, 0)
        self.status_indicator.setGraphicsEffect(self.glow_indicator)

        status_container.addWidget(status_label)
        status_container.addWidget(self.status_value)
        status_container.addWidget(self.status_indicator)
        status_container.setSpacing(0)

        layout.addLayout(status_container)

    def update_status(self, status_text, color):
        self.status_value.setText(status_text)
        self.status_value.setStyleSheet(f"background: transparent; color: {color}; font-size: 16px; font-weight: bold; padding: 0px 5px; border: none; letter-spacing: 2px;")
        self.status_indicator.setStyleSheet(f"background: transparent; color: {color}; font-size: 20px; padding: 0px; border: none;")
        # Actualizar color del glow
        self.glow_effect.setColor(QColor(color))
        self.glow_indicator.setColor(QColor(color))


class TelemetryPanel(MetalPanel):
    def __init__(self, parent=None):
        super().__init__("TELEMETRY CLUSTER", parent)
        self.setFixedWidth(350)
        layout = self.get_content_layout()

        self.altitude = DataDisplay("ALTITUDE ASL (M)", "0.0", "m", show_graph=True)
        self.velocity = DataDisplay("VELOCITY (M/S)", "0.0", "m/s", show_graph=True)
        self.acceleration = DataDisplay("ACCELERATION (g)", "0.0", "g", show_graph=False)
        self.temperature = DataDisplay("TEMPERATURE (°C)", "0.0", "°C", show_graph=False)
        self.pressure = DataDisplay("PRESSURE (hPa)", "0.0", "hPa", show_graph=False)

        layout.addWidget(self.altitude)
        layout.addWidget(self.velocity)
        layout.addWidget(self.acceleration)
        layout.addWidget(self.temperature)
        layout.addWidget(self.pressure)

        # System Logs dentro del cluster
        from ui.widgets import LogConsole
        log_title = QLabel("SYSTEM LOGS")
        log_title.setStyleSheet("color: #c9d1d9; font-size: 11px; font-weight: bold; background: transparent; border: none; letter-spacing: 1px; padding-top: 4px;")
        log_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(log_title)
        self.sys_log = LogConsole()
        layout.addWidget(self.sys_log, stretch=1)

    def update_data(self, alt, vel, acc, temp, pressure=1013.25):
        # Calcular altitud ASL desde presión barométrica
        alt_asl = 44330.0 * (1.0 - math.pow(pressure / 1013.25, 1.0 / 5.255))
        self.altitude.update_value(f"{alt_asl:.1f}")
        self.altitude.push_value(alt_asl)
        self.velocity.update_value(f"{vel:.1f}")
        self.velocity.push_value(vel)
        self.acceleration.update_value(f"{acc:.1f}")
        self.temperature.update_value(f"{temp:.1f}")

    def update_pressure(self, pressure):
        self.pressure.update_value(f"{pressure:.1f}")

    def clear_data(self):
        self.altitude.clear_data()
        self.velocity.clear_data()
        self.acceleration.clear_data()
        self.temperature.clear_data()
        self.pressure.clear_data()
        self.sys_log.clear_logs()


# --- PANEL DE GRÁFICAS: ALTITUD Y VELOCIDAD ---
class GraphPanel(MetalPanel):
    def __init__(self, parent=None):
        super().__init__("RELATIVE ALTITUDE vs TIME", parent)
        layout = self.get_content_layout()

        # Configuración visual de pyqtgraph
        pg.setConfigOption('background', '#0d1117')
        pg.setConfigOption('foreground', '#8b949e')

        # --- Gráfica de ALTITUD ---
        alt_label = QLabel("▲ RELATIVE ALTITUDE (m)")
        alt_label.setStyleSheet("color: #58a6ff; font-size: 11px; font-weight: bold; background: transparent; border: none; padding: 4px 0px 2px 0px;")
        layout.addWidget(alt_label)

        self.alt_widget = pg.PlotWidget()
        self.alt_widget.showGrid(x=True, y=True, alpha=0.3)
        self.alt_widget.setLabel('left', 'm')
        self.alt_widget.setLabel('bottom', 'Time (s)')
        self.alt_widget.setStyleSheet("border: 1px solid #30363d; border-radius: 6px; background-color: #0d1117;")
        self.time_data = []
        self.altitude_data = []
        self.deploy_data = []  # 0 o 1

        # Región de despliegue (fill verde semitransparente)
        deploy_pen = pg.mkPen(color='#3fb95066', width=0)
        deploy_brush = pg.mkBrush('#3fb95033')
        self.deploy_fill = self.alt_widget.plot([], [], pen=deploy_pen, fillLevel=0, brush=deploy_brush, name='Deployed')

        # Línea de altitud (encima de la banda de despliegue)
        alt_pen = pg.mkPen(color='#58a6ff', width=2)
        self.alt_line = self.alt_widget.plot(self.time_data, self.altitude_data, pen=alt_pen, name='Altitude')

        # Leyenda
        legend = self.alt_widget.addLegend(offset=(10, 10))
        legend.setLabelTextColor('#8b949e')

        # Indicador de estado de despliegue
        self.deploy_label = QLabel("🔒 STOWED")
        self.deploy_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: bold; background: transparent; border: none; padding: 2px 0px;")
        self.deploy_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.deploy_label)

        layout.addWidget(self.alt_widget)

    def update_graph(self, current_time, altitude, deployed=False):
        self.time_data.append(current_time)
        self.altitude_data.append(altitude)
        # Escalar el deploy al valor de altitud actual para que la banda llene hasta la curva
        self.deploy_data.append(altitude if deployed else 0)

        # Mantener solo los últimos 100 puntos (scrolling)
        if len(self.time_data) > 100:
            self.time_data = self.time_data[-100:]
            self.altitude_data = self.altitude_data[-100:]
            self.deploy_data = self.deploy_data[-100:]

        self.alt_line.setData(self.time_data, self.altitude_data)
        self.deploy_fill.setData(self.time_data, self.deploy_data)

        # Actualizar indicador textual
        if deployed:
            self.deploy_label.setText("🪂 DEPLOYED")
            self.deploy_label.setStyleSheet("color: #3fb950; font-size: 11px; font-weight: bold; background: transparent; border: none; padding: 2px 0px;")
        else:
            self.deploy_label.setText("🔒 STOWED")
            self.deploy_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: bold; background: transparent; border: none; padding: 2px 0px;")

    def clear_graph(self):
        self.time_data.clear()
        self.altitude_data.clear()
        self.deploy_data.clear()
        self.alt_line.setData(self.time_data, self.altitude_data)
        self.deploy_fill.setData(self.time_data, self.deploy_data)
        self.deploy_label.setText("🔒 STOWED")
        self.deploy_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: bold; background: transparent; border: none; padding: 2px 0px;")


class ControlPanel(MetalPanel):
    connection_toggled = Signal(bool, str)
    refresh_requested = Signal()
    simulate_toggled = Signal(bool)
    clear_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("CONTROL COM", parent)
        self.is_connected = False
        self.is_simulating = False
        layout = self.get_content_layout()

        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.setStyleSheet(styles.COMBOBOX_STYLE)

        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedWidth(30)
        self.btn_refresh.setStyleSheet("QPushButton { background: rgba(33,38,45,230); color: #c9d1d9; border: 1px solid rgba(48,54,61,0.7); border-radius: 6px; padding: 4px; } QPushButton:hover { background: rgba(48,54,61,230); }")
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)

        port_layout.addWidget(self.port_combo, stretch=1)
        port_layout.addWidget(self.btn_refresh)

        self.btn_connect = QPushButton("▶  CONNECT SERIAL")
        self.btn_connect.setStyleSheet(styles.BUTTON_PRIMARY_STYLE)
        self.btn_connect.clicked.connect(self.toggle)

        self.btn_simulate = QPushButton("◉  SIMULATE DATA")
        self.btn_simulate.setStyleSheet(styles.BUTTON_SECONDARY_STYLE)
        self.btn_simulate.clicked.connect(self.toggle_simulate)

        self.btn_clear = QPushButton("✕  CLEAR DATA")
        self.btn_clear.setStyleSheet(styles.BUTTON_DANGER_STYLE)
        self.btn_clear.clicked.connect(self.clear_requested.emit)

        layout.addLayout(port_layout)
        layout.addWidget(self.btn_connect)
        layout.addWidget(self.btn_simulate)
        layout.addWidget(self.btn_clear)

    def update_ports(self, port_list):
        self.port_combo.clear()
        if port_list:
            self.port_combo.addItems(port_list)
        else:
            self.port_combo.addItem("NO PORTS FOUND")

    def toggle(self):
        port_name = self.port_combo.currentText()
        if port_name == "NO PORTS FOUND" or not port_name:
            return

        self.is_connected = not self.is_connected
        if self.is_connected:
            self.btn_connect.setText("⏸️ DISCONNECT")
            # Bloquear todo excepto disconnect y clear
            self.port_combo.setEnabled(False)
            self.btn_refresh.setEnabled(False)
            self.btn_simulate.setEnabled(False)
            self.btn_simulate.setStyleSheet(styles.BUTTON_DISABLED_STYLE)
            # Detener simulación si estaba activa
            if self.is_simulating:
                self.toggle_simulate()
        else:
            self.btn_connect.setText("▶  CONNECT SERIAL")
            # Re-habilitar todo
            self.port_combo.setEnabled(True)
            self.btn_refresh.setEnabled(True)
            self.btn_simulate.setEnabled(True)
            self.btn_simulate.setStyleSheet(styles.BUTTON_SECONDARY_STYLE)

        self.connection_toggled.emit(self.is_connected, port_name)
        self.update_clear_button_state()

    def toggle_simulate(self):
        self.is_simulating = not self.is_simulating
        if self.is_simulating:
            self.btn_simulate.setText("■  STOP SIMULATION")
            self.btn_simulate.setStyleSheet(styles.BUTTON_ACTIVE_STYLE)
            # Bloquear serial, refresh y port mientras se simula
            self.btn_connect.setEnabled(False)
            self.btn_connect.setStyleSheet(styles.BUTTON_DISABLED_STYLE)
            self.port_combo.setEnabled(False)
            self.btn_refresh.setEnabled(False)
        else:
            self.btn_simulate.setText("◉  SIMULATE DATA")
            self.btn_simulate.setStyleSheet(styles.BUTTON_SECONDARY_STYLE)
            # Re-habilitar serial
            self.btn_connect.setEnabled(True)
            self.btn_connect.setStyleSheet(styles.BUTTON_PRIMARY_STYLE)
            self.port_combo.setEnabled(True)
            self.btn_refresh.setEnabled(True)

        self.simulate_toggled.emit(self.is_simulating)
        self.update_clear_button_state()

    def update_clear_button_state(self):
        if self.is_connected or self.is_simulating:
            self.btn_clear.setEnabled(False)
            self.btn_clear.setStyleSheet(styles.BUTTON_DISABLED_STYLE)
        else:
            self.btn_clear.setEnabled(True)
            self.btn_clear.setStyleSheet(styles.BUTTON_DANGER_STYLE)


class CompassWidget(QWidget):
    """Widget personalizado que dibuja una brújula animada."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self._heading = 0.0
        self.animation = QPropertyAnimation(self, b"heading_prop")
        self.animation.setDuration(200) # 200ms para rotación suave

    @Property(float)
    def heading_prop(self):
        return self._heading

    @heading_prop.setter
    def heading_prop(self, val):
        self._heading = val
        self.update()  # Forzar repintado al cambiar el valor

    def set_heading(self, target_heading):
        # Evitar giro completo cuando pasa de 359 a 0
        current = self._heading % 360
        target = target_heading % 360
        
        diff = target - current
        if diff > 180:
            target -= 360
        elif diff < -180:
            target += 360
            
        self.animation.stop()
        self.animation.setStartValue(self._heading)
        self.animation.setEndValue(target)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Trasladar al centro
        w, h = self.width(), self.height()
        painter.translate(w / 2, h / 2)
        
        # Dibujar anillo exterior
        painter.setPen(QPen(QColor("#30363d"), 2))
        painter.setBrush(QColor("#0d1117"))
        radius = min(w, h) / 2 - 2
        painter.drawEllipse(-radius, -radius, radius * 2, radius * 2)

        # Letras N,S,E,W
        painter.setPen(QColor("#8b949e"))
        font = QFont("Consolas", 8, QFont.Bold)
        painter.setFont(font)
        text_r = radius - 10
        painter.drawText(-5, -text_r + 5, "N")
        painter.drawText(-5, text_r + 5, "S")
        painter.drawText(text_r - 8, 4, "E")
        painter.drawText(-text_r, 4, "W")
        
        # Rotar el canvas según el heading (el Norte arriba, así que rotamos la aguja)
        painter.rotate(self._heading)
        
        # Dibujar aguja (Norte = Rojo, Sur = Blanco/Gris)
        # Parte Norte (Roja)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#ff5252"))
        north_poly = QPolygon([
            QPoint(0, int(-radius + 15)),  # Punta superior
            QPoint(4, 0),         # Centro derecha
            QPoint(-4, 0)         # Centro izquierda
        ])
        painter.drawPolygon(north_poly)
        
        # Parte Sur (Gris)
        painter.setBrush(QColor("#8b949e"))
        south_poly = QPolygon([
            QPoint(0, int(radius - 15)),   # Punta inferior
            QPoint(4, 0),         # Centro derecha
            QPoint(-4, 0)         # Centro izquierda
        ])
        painter.drawPolygon(south_poly)
        
        # Centro
        painter.setBrush(QColor("#c9d1d9"))
        painter.drawEllipse(-2, -2, 4, 4)
        
        painter.end()


class FooterPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # --- BATTERY (izquierda) ---
        b_panel = MetalPanel("BATTERY")
        b_container = QFrame()
        b_container.setStyleSheet("background-color: #0d1117; border-radius: 6px;")
        b_layout = QHBoxLayout(b_container)
        self.battery_bar = QLabel("░" * 20)
        self.battery_value = QLabel("0 %")
        self.battery_bar.setStyleSheet("color: #ff5252; font-size: 20px; background: transparent; border: none;")
        self.battery_value.setStyleSheet("color: #ff5252; font-size: 24px; font-weight: bold; font-family: 'Consolas', monospace; background: transparent; border: none;")
        b_layout.addWidget(self.battery_bar)
        b_layout.addWidget(self.battery_value)
        b_panel.get_content_layout().addWidget(b_container)
        layout.addWidget(b_panel, stretch=1)

        # --- HEADING / MAGNETOMETRO (centro) ---
        h_panel = MetalPanel("HEADING (MAG)")
        h_inner = QWidget()
        h_inner.setStyleSheet("background: transparent;")
        h_inner_layout = QHBoxLayout(h_inner)
        h_inner_layout.setContentsMargins(0, 0, 0, 0)
        h_inner_layout.setSpacing(8)

        self.compass_widget = CompassWidget()

        self.heading_display = QLabel("0.0\u00b0")
        self.heading_display.setStyleSheet(
            "background-color: #0d1117; color: #58a6ff; font-size: 32px; font-weight: bold;"
            " font-family: 'Consolas', monospace; padding: 15px; border-radius: 6px; border: none;"
        )
        self.heading_display.setAlignment(Qt.AlignCenter)

        h_inner_layout.addWidget(self.compass_widget)
        h_inner_layout.addWidget(self.heading_display, stretch=1)
        h_panel.get_content_layout().addWidget(h_inner)
        layout.addWidget(h_panel, stretch=1)

        # --- GPS (derecha) ---
        gps_panel = MetalPanel("GPS COORDINATES")
        self.gps_display = QLabel("LAT: 0.0000\u00b0\nLON: 0.0000\u00b0")
        self.gps_display.setStyleSheet(
            "background-color: #0d1117; color: #58a6ff; font-size: 18px; font-weight: bold;"
            " font-family: 'Consolas', monospace; padding: 15px; border-radius: 6px; border: none;"
        )
        self.gps_display.setAlignment(Qt.AlignCenter)
        gps_panel.get_content_layout().addWidget(self.gps_display)
        layout.addWidget(gps_panel, stretch=1)

    def update_battery(self, battery):
        bars = int(battery / 5)
        self.battery_bar.setText("\u2593" * bars + "\u2591" * (20 - bars))
        self.battery_value.setText(f"{int(battery)} %")
        color = "#4caf50" if battery > 50 else "#ffb74d" if battery > 20 else "#ff5252"
        self.battery_bar.setStyleSheet(f"color: {color}; font-size: 20px; background: transparent; border: none;")
        self.battery_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; font-family: 'Consolas', monospace; background: transparent; border: none;")

    def update_heading(self, heading):
        """heading en grados 0-360, actualiza animación de brújula y valor textual."""
        self.compass_widget.set_heading(heading)
        self.heading_display.setText(f"{heading:.1f}\u00b0")

    def update_gps(self, latitude, longitude):
        """Actualiza las coordenadas GPS en el display."""
        lat_dir = "N" if latitude >= 0 else "S"
        lon_dir = "E" if longitude >= 0 else "W"
        self.gps_display.setText(
            f"LAT: {abs(latitude):.4f}\u00b0 {lat_dir}\nLON: {abs(longitude):.4f}\u00b0 {lon_dir}"
        )