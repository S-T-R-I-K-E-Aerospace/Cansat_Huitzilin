#!/usr/bin/env python3
"""
S.T.R.I.K.E Aerospace - Mission Control v2.3.1
Versión Standalone (sin dependencias externas)

Esta versión funciona sin necesidad de panel_telemetria, panel_imagen o comunicacion_serial.
Ideal para probar el diseño y como base para tu integración.
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QPushButton, QLabel, QMessageBox, 
                               QComboBox, QFrame, QGridLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

class DataDisplay(QFrame):
    """Widget para mostrar datos con fondo oscuro"""
    def __init__(self, label="", value="", unit="", show_graph=False, parent=None):
        super().__init__(parent)
        self.label_text = label
        self.value_text = value
        self.unit_text = unit
        self.show_graph = show_graph
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            DataDisplay {
                background-color: #0d1117;
                border: 2px solid #30363d;
                border-radius: 6px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Contenedor de texto
        text_container = QVBoxLayout()
        text_container.setSpacing(2)
        
        # Label
        if self.label_text:
            label = QLabel(self.label_text)
            label.setStyleSheet("""
                color: #8b949e;
                font-size: 10px;
                font-weight: bold;
                background: transparent;
                border: none;
            """)
            text_container.addWidget(label)
        
        # Valor
        self.value_label = QLabel(self.value_text + " " + self.unit_text)
        self.value_label.setStyleSheet("""
            color: #ffffff;
            font-size: 28px;
            font-weight: bold;
            font-family: 'Consolas', 'Courier New', monospace;
            background: transparent;
            border: none;
        """)
        text_container.addWidget(self.value_label)
        
        layout.addLayout(text_container)
        
        # Mini gráfico (placeholder)
        if self.show_graph:
            graph_label = QLabel("📊")
            graph_label.setStyleSheet("""
                color: #58a6ff;
                font-size: 40px;
                background: transparent;
                border: none;
            """)
            layout.addWidget(graph_label)
            
    def update_value(self, value, unit=""):
        """Actualiza el valor mostrado"""
        self.value_label.setText(f"{value} {unit if unit else self.unit_text}")


class MetalPanel(QFrame):
    """Panel con efecto metálico y bordes biselados"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
        
    def setup_ui(self):
        # Estilo metálico con bordes biselados
        self.setStyleSheet("""
            MetalPanel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c8c8c8, stop:0.5 #a0a0a0, stop:1 #888888);
                border: 3px outset #b0b0b0;
                border-radius: 12px;
            }
        """)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)
        
        # Título del panel
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet("""
                color: #1a1a1a;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
                text-transform: uppercase;
                letter-spacing: 1px;
            """)
            title_label.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(title_label)
            
    def get_content_layout(self):
        """Retorna el layout para agregar contenido"""
        return self.main_layout


class EstacionTerrena(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S.T.R.I.K.E Aerospace - Mission Control v2.3.1")
        self.resize(1400, 900)
        self.lector_serial = None
        self.mission_elapsed_time = 0  # Tiempo en segundos
        self.simulacion_activa = False
        
        # Estilo general
        self.setStyleSheet("""
            QMainWindow { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # HEADER
        header = self.create_header()
        main_layout.addWidget(header)
        
        # BODY (3 columnas)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(10)
        
        # Columna izquierda: Telemetría
        left_panel = self.create_left_panel()
        body_layout.addWidget(left_panel)
        
        # Columna central: Gráfico de altitud
        center_panel = self.create_center_panel()
        body_layout.addWidget(center_panel, stretch=1)
        
        # Columna derecha: Cámaras y estado
        right_panel = self.create_right_panel()
        body_layout.addWidget(right_panel)
        
        main_layout.addLayout(body_layout, stretch=1)
        
        # FOOTER
        footer = self.create_footer()
        main_layout.addLayout(footer)
        
        # Timer para MET (Mission Elapsed Time)
        self.met_timer = QTimer()
        self.met_timer.timeout.connect(self.update_met)
        self.met_timer.start(1000)  # Actualizar cada segundo
        
        # Timer para simulación de datos
        self.sim_timer = QTimer()
        self.sim_timer.timeout.connect(self.simulate_data)
        
    def create_header(self):
        """Crea el header con logo, misión, MET y status"""
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d0d0d0, stop:0.5 #b0b0b0, stop:1 #909090);
                border: 3px outset #c0c0c0;
                border-radius: 15px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Logo y nombre
        logo_container = QVBoxLayout()
        logo_label = QLabel("🚀")
        logo_label.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        brand_label = QLabel("S.T.R.I.K.E\nAEROSPACE")
        brand_label.setStyleSheet("""
            color: #1a1a1a;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Arial', sans-serif;
            background: transparent;
            border: none;
            line-height: 1.2;
        """)
        logo_container.addWidget(logo_label, alignment=Qt.AlignCenter)
        logo_container.addWidget(brand_label, alignment=Qt.AlignCenter)
        layout.addLayout(logo_container)
        
        layout.addStretch()
        
        # Misión
        mission_label = QLabel("MISSION: CANSAT WORLD CUP 2026")
        mission_label.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            padding: 12px 24px;
            border-radius: 8px;
            border: 2px solid #30363d;
        """)
        layout.addWidget(mission_label)
        
        layout.addStretch()
        
        # MET (Mission Elapsed Time)
        self.met_label = QLabel("MET: +00:00:00")
        self.met_label.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            padding: 12px 24px;
            border-radius: 8px;
            border: 2px solid #30363d;
            font-family: 'Consolas', monospace;
        """)
        layout.addWidget(self.met_label)
        
        layout.addStretch()
        
        # Status
        status_container = QHBoxLayout()
        status_label = QLabel("STATUS:")
        status_label.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            padding: 12px 20px 12px 24px;
            border-radius: 8px 0px 0px 8px;
            border: 2px solid #30363d;
            border-right: none;
        """)
        
        self.status_value = QLabel("DISCONNECTED")
        self.status_value.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ff5252;
            font-size: 16px;
            font-weight: bold;
            padding: 12px 10px 12px 5px;
            border-radius: 0px;
            border: 2px solid #30363d;
            border-left: none;
            border-right: none;
        """)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ff5252;
            font-size: 24px;
            padding: 8px 24px 8px 10px;
            border-radius: 0px 8px 8px 0px;
            border: 2px solid #30363d;
            border-left: none;
        """)
        
        status_container.addWidget(status_label)
        status_container.addWidget(self.status_value)
        status_container.addWidget(self.status_indicator)
        status_container.setSpacing(0)
        
        layout.addLayout(status_container)
        
        return header
    
    def create_left_panel(self):
        """Panel izquierdo con cluster de telemetría"""
        panel = MetalPanel("TELEMETRY CLUSTER")
        layout = panel.get_content_layout()
        
        # Altitud
        self.altitude_display = DataDisplay("ALTITUDE (M)", "0.0", "m", show_graph=True)
        layout.addWidget(self.altitude_display)
        
        # Velocidad
        self.velocity_display = DataDisplay("VELOCITY (M/S)", "0.0", "m/s", show_graph=True)
        layout.addWidget(self.velocity_display)
        
        # Aceleración
        self.acceleration_display = DataDisplay("ACCELERATION (g)", "0.0", "g", show_graph=False)
        layout.addWidget(self.acceleration_display)
        
        # Temperatura
        self.temperature_display = DataDisplay("TEMPERATURE (°C)", "0.0", "°C", show_graph=False)
        layout.addWidget(self.temperature_display)
        
        layout.addStretch()
        
        panel.setFixedWidth(350)
        return panel
    
    def create_center_panel(self):
        """Panel central con gráfico de altitud vs tiempo"""
        panel = MetalPanel("ALTITUDE vs TIME")
        layout = panel.get_content_layout()
        
        # Placeholder para el gráfico
        graph_container = QFrame()
        graph_container.setStyleSheet("""
            background-color: #0d1117;
            border: 2px solid #30363d;
            border-radius: 6px;
        """)
        
        graph_layout = QVBoxLayout(graph_container)
        graph_label = QLabel("📈 ALTITUDE GRAPH")
        graph_label.setStyleSheet("""
            color: #58a6ff;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        graph_label.setAlignment(Qt.AlignCenter)
        
        # Info del gráfico
        info_label = QLabel("Peak: 1310m @ 80s\nFW: v2.3.1")
        info_label.setStyleSheet("""
            color: #8b949e;
            font-size: 10px;
            background: transparent;
            border: none;
        """)
        info_label.setAlignment(Qt.AlignRight)
        
        graph_layout.addWidget(info_label, alignment=Qt.AlignRight)
        graph_layout.addStretch()
        graph_layout.addWidget(graph_label)
        graph_layout.addStretch()
        
        layout.addWidget(graph_container)
        
        return panel
    
    def create_right_panel(self):
        """Panel derecho con cámaras y estado del sistema"""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Panel de cámaras estereoscópicas
        camera_panel = MetalPanel("STEREOSCOPIC CANSAT MONITOR")
        cam_layout = camera_panel.get_content_layout()
        
        cameras_grid = QHBoxLayout()
        cameras_grid.setSpacing(10)
        
        # Cámara izquierda
        left_cam = self.create_camera_view("LEFT (L) CAM")
        cameras_grid.addWidget(left_cam)
        
        # Cámara derecha
        right_cam = self.create_camera_view("RIGHT (R) CAM")
        cameras_grid.addWidget(right_cam)
        
        cam_layout.addLayout(cameras_grid)
        main_layout.addWidget(camera_panel)
        
        # Panel de estado del sistema
        status_panel = MetalPanel()
        status_layout = status_panel.get_content_layout()
        
        sd_status = QLabel("• SD Logging: <span style='color: #4caf50;'>WRITING</span>")
        sd_status.setStyleSheet("""
            color: #ffffff;
            font-size: 13px;
            font-weight: bold;
            background: #0d1117;
            padding: 10px;
            border-radius: 6px;
            border: none;
        """)
        
        autogyro_status = QLabel("• Autogyro deployed: <span style='color: #4caf50;'>ACTIVE at 01:22</span>")
        autogyro_status.setStyleSheet("""
            color: #ffffff;
            font-size: 13px;
            font-weight: bold;
            background: #0d1117;
            padding: 10px;
            border-radius: 6px;
            border: none;
        """)
        
        status_layout.addWidget(sd_status)
        status_layout.addWidget(autogyro_status)
        
        # Panel de control
        control_panel = MetalPanel("CONTROL")
        ctrl_layout = control_panel.get_content_layout()
        
        self.btn_simular = QPushButton("▶️ START SIMULATION")
        self.btn_simular.setStyleSheet("""
            QPushButton {
                background-color: #1f6feb;
                color: white;
                border: 2px solid #388bfd;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388bfd;
            }
        """)
        self.btn_simular.clicked.connect(self.toggle_simulacion)
        ctrl_layout.addWidget(self.btn_simular)
        
        main_layout.addWidget(status_panel)
        main_layout.addWidget(control_panel)
        main_layout.addStretch()
        
        container.setFixedWidth(450)
        return container
    
    def create_camera_view(self, title):
        """Crea un visor de cámara"""
        frame = QFrame()
        frame.setStyleSheet("""
            background-color: #0d1117;
            border: 2px solid #30363d;
            border-radius: 6px;
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Indicador de grabación
        rec_label = QLabel("🔴 REC ACTIVE")
        rec_label.setStyleSheet("""
            color: #ff4444;
            font-size: 10px;
            font-weight: bold;
            background: rgba(255, 68, 68, 0.2);
            padding: 4px 8px;
            border-radius: 4px;
            border: none;
        """)
        layout.addWidget(rec_label)
        
        # Área de imagen
        img_placeholder = QLabel("📷")
        img_placeholder.setStyleSheet("""
            color: #30363d;
            font-size: 48px;
            background: #000000;
            border: 1px solid #30363d;
            border-radius: 4px;
        """)
        img_placeholder.setAlignment(Qt.AlignCenter)
        img_placeholder.setMinimumSize(180, 140)
        layout.addWidget(img_placeholder)
        
        # Descripción
        desc_label = QLabel("3D VIEW: SIDE-BY-SIDE (SPS)")
        desc_label.setStyleSheet("""
            color: #8b949e;
            font-size: 9px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        return frame
    
    def create_footer(self):
        """Crea el footer con paneles de información"""
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(10)
        
        # Presión
        pressure_panel = MetalPanel("PRESSURE (hPa)")
        pressure_layout = pressure_panel.get_content_layout()
        self.pressure_display = QLabel("892.4 hPa")
        self.pressure_display.setStyleSheet("""
            background-color: #0d1117;
            color: #ffffff;
            font-size: 32px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
            padding: 15px;
            border-radius: 6px;
            border: none;
        """)
        self.pressure_display.setAlignment(Qt.AlignCenter)
        pressure_layout.addWidget(self.pressure_display)
        footer_layout.addWidget(pressure_panel)
        
        # Batería
        battery_panel = MetalPanel("BATTERY")
        battery_layout = battery_panel.get_content_layout()
        battery_container = QFrame()
        battery_container.setStyleSheet("""
            background-color: #0d1117;
            border-radius: 6px;
        """)
        bat_layout = QHBoxLayout(battery_container)
        
        # Barra de batería
        self.battery_bar = QLabel("▓" * 20)
        self.battery_bar.setStyleSheet("""
            color: #4caf50;
            font-size: 20px;
            background: transparent;
            border: none;
        """)
        
        self.battery_value = QLabel("78 %")
        self.battery_value.setStyleSheet("""
            color: #4caf50;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
            background: transparent;
            border: none;
        """)
        
        bat_layout.addWidget(self.battery_bar)
        bat_layout.addWidget(self.battery_value)
        battery_layout.addWidget(battery_container)
        footer_layout.addWidget(battery_panel)
        
        # GPS
        gps_panel = MetalPanel("GPS COORDINATES")
        gps_layout = gps_panel.get_content_layout()
        self.gps_display = QLabel("LAT: 34.0211° N\nLON: -118.4902° W")
        self.gps_display.setStyleSheet("""
            background-color: #0d1117;
            color: #58a6ff;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
            padding: 15px;
            border-radius: 6px;
            border: none;
        """)
        self.gps_display.setAlignment(Qt.AlignCenter)
        gps_layout.addWidget(self.gps_display)
        footer_layout.addWidget(gps_panel)
        
        # Orientación
        orientation_panel = MetalPanel("ORIENTATION (Roll Pitch Yaw)")
        orient_layout = orientation_panel.get_content_layout()
        orient_container = QHBoxLayout()
        
        # Indicador artificial (placeholder)
        indicator = QLabel("🎯")
        indicator.setStyleSheet("""
            background-color: #0d1117;
            color: #58a6ff;
            font-size: 48px;
            padding: 10px;
            border-radius: 6px;
        """)
        
        # Valores
        self.orientation_values = QLabel("ROLL: -2.1°\nPITCH: +5.3°\nYAW: 110.8°")
        self.orientation_values.setStyleSheet("""
            background-color: #0d1117;
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
            padding: 10px;
            border-radius: 6px;
            border: none;
        """)
        
        orient_container.addWidget(indicator)
        orient_container.addWidget(self.orientation_values)
        orient_layout.addLayout(orient_container)
        footer_layout.addWidget(orientation_panel)
        
        return footer_layout
    
    def update_met(self):
        """Actualiza el Mission Elapsed Time"""
        self.mission_elapsed_time += 1
        hours = self.mission_elapsed_time // 3600
        minutes = (self.mission_elapsed_time % 3600) // 60
        seconds = self.mission_elapsed_time % 60
        self.met_label.setText(f"MET: +{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def update_status(self, status_text, color):
        """Actualiza el estado de conexión"""
        self.status_value.setText(status_text)
        self.status_value.setStyleSheet(f"""
            background-color: #1a1a1a;
            color: {color};
            font-size: 16px;
            font-weight: bold;
            padding: 12px 10px 12px 5px;
            border-radius: 0px;
            border: 2px solid #30363d;
            border-left: none;
            border-right: none;
        """)
        self.status_indicator.setStyleSheet(f"""
            background-color: #1a1a1a;
            color: {color};
            font-size: 24px;
            padding: 8px 24px 8px 10px;
            border-radius: 0px 8px 8px 0px;
            border: 2px solid #30363d;
            border-left: none;
        """)
    
    def toggle_simulacion(self):
        """Alterna el modo de simulación"""
        if not self.simulacion_activa:
            self.simulacion_activa = True
            self.sim_timer.start(100)  # Actualizar cada 100ms
            self.btn_simular.setText("⏸️ STOP SIMULATION")
            self.update_status("SIMULATING", "#ffb74d")
        else:
            self.simulacion_activa = False
            self.sim_timer.stop()
            self.btn_simular.setText("▶️ START SIMULATION")
            self.update_status("DISCONNECTED", "#ff5252")
    
    def simulate_data(self):
        """Simula datos de telemetría"""
        import random
        import math
        
        # Simular una trayectoria parabólica
        t = self.mission_elapsed_time % 120  # Ciclo de 120 segundos
        
        # Altitud (parabólica)
        altitude = -0.5 * (t - 80)**2 + 1310
        altitude = max(0, altitude)
        
        # Velocidad (derivada de la altitud)
        velocity = abs(-(t - 80) + random.uniform(-5, 5))
        
        # Aceleración
        acceleration = random.uniform(0.8, 2.5)
        
        # Temperatura
        temperature = 20 - (altitude / 100) + random.uniform(-1, 1)
        
        # Actualizar displays
        self.altitude_display.update_value(f"{altitude:.1f}", "m")
        self.velocity_display.update_value(f"{velocity:.1f}", "m/s")
        self.acceleration_display.update_value(f"{acceleration:.1f}", "g")
        self.temperature_display.update_value(f"{temperature:.1f}", "°C")
        
        # Actualizar presión
        pressure = 1013.25 * math.exp(-altitude / 8500)
        self.pressure_display.setText(f"{pressure:.1f} hPa")
        
        # Batería (decrece lentamente)
        battery = max(0, 100 - self.mission_elapsed_time / 10)
        bars = int(battery / 5)
        self.battery_bar.setText("▓" * bars + "░" * (20 - bars))
        self.battery_value.setText(f"{int(battery)} %")
        
        # Actualizar color de batería
        if battery > 50:
            color = "#4caf50"
        elif battery > 20:
            color = "#ffb74d"
        else:
            color = "#ff5252"
        
        self.battery_bar.setStyleSheet(f"color: {color}; font-size: 20px; background: transparent; border: none;")
        self.battery_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; font-family: 'Consolas', monospace; background: transparent; border: none;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Mensaje de bienvenida
    print("=" * 60)
    print("🚀 S.T.R.I.K.E Aerospace - Mission Control v2.3.1")
    print("=" * 60)
    print("✅ Versión Standalone - Sin dependencias externas")
    print("📊 Haz clic en 'START SIMULATION' para ver datos en tiempo real")
    print("=" * 60)
    
    w = EstacionTerrena()
    w.show()
    sys.exit(app.exec())