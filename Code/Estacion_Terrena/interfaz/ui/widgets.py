# ui/widgets.py
import os
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QTextCursor
from ui import styles
import pyqtgraph as pg

class DataDisplay(QFrame):
    def __init__(self, label="", value="", unit="", show_graph=False, graph_label="", parent=None):
        super().__init__(parent)
        self.label_text = label
        self.value_text = value
        self.unit_text = unit
        self.show_graph = show_graph
        self.graph_label = graph_label
        self._history = []
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(styles.DATA_DISPLAY_STYLE)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        text_container = QVBoxLayout()
        text_container.setSpacing(2)

        if self.label_text:
            label = QLabel(self.label_text)
            label.setStyleSheet(styles.DATA_LABEL_STYLE)
            text_container.addWidget(label)

        self.value_label = QLabel(f"{self.value_text} {self.unit_text}")
        self.value_label.setStyleSheet(styles.DATA_VALUE_STYLE)
        text_container.addWidget(self.value_label)

        layout.addLayout(text_container)

        if self.show_graph:
            # Elegir color según la unidad
            color = '#3fb950' if 'm/s' in self.unit_text else '#58a6ff'

            pg.setConfigOption('background', '#161b22')
            pg.setConfigOption('foreground', '#8b949e')

            graph_container = QVBoxLayout()
            graph_container.setSpacing(0)
            graph_container.setContentsMargins(0, 0, 0, 0)

            if self.graph_label:
                g_label = QLabel(self.graph_label)
                g_label.setStyleSheet("color: #8b949e; font-size: 8px; font-weight: bold; background: transparent; border: none; letter-spacing: 1px;")
                g_label.setAlignment(Qt.AlignCenter)
                graph_container.addWidget(g_label)

            self.mini_plot = pg.PlotWidget()
            self.mini_plot.setFixedSize(185, 90)
            self.mini_plot.hideAxis('left')
            self.mini_plot.hideAxis('bottom')
            self.mini_plot.showGrid(x=False, y=True, alpha=0.2)
            self.mini_plot.setMouseEnabled(x=False, y=False)
            self.mini_plot.setMenuEnabled(False)
            self.mini_plot.setStyleSheet(styles.MINI_GRAPH_STYLE)

            pen = pg.mkPen(color=color, width=2)
            fill = pg.mkBrush(color + '33')  # Relleno translúcido
            self._curve = self.mini_plot.plot([], [], pen=pen, fillLevel=0, brush=fill)

            graph_container.addWidget(self.mini_plot)
            layout.addLayout(graph_container)

    def update_value(self, value, unit=""):
        self.value_label.setText(f"{value} {unit if unit else self.unit_text}")

    def push_value(self, value: float):
        """Añade un valor a la mini gráfica (llamar junto con update_value)."""
        if not self.show_graph:
            return
        self._history.append(value)
        if len(self._history) > 60:
            self._history = self._history[-60:]
        self._curve.setData(self._history)

    def clear_data(self):
        self.update_value("0.0")
        if self.show_graph:
            self._history.clear()
            self._curve.setData([])


class MetalPanel(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet(styles.METAL_PANEL_STYLE)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet("color: #c9d1d9; font-size: 13px; font-weight: bold; font-family: 'Arial', sans-serif; background: transparent; border: none; text-transform: uppercase; letter-spacing: 1px;")
            title_label.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(title_label)
            
    def get_content_layout(self):
        return self.main_layout

class CameraView(QFrame):
    log_message = Signal(str)

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet(styles.CAMERA_FRAME_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        self.img_label = QLabel("Waiting for image...")
        self.img_label.setStyleSheet("color: #30363d; font-size: 15px; background: #000000; border: 1px solid #30363d; border-radius: 4px;")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setMinimumSize(180, 140)
        self.img_label.setScaledContents(False)
        layout.addWidget(self.img_label)
        
        # Info inferior: título + timestamp
        info_layout = QHBoxLayout()
        desc_label = QLabel(title)
        desc_label.setStyleSheet("color: #8b949e; font-size: 9px; font-weight: bold; background: transparent; border: none;")
        
        self.time_label = QLabel("")
        self.time_label.setStyleSheet("color: #484f58; font-size: 9px; background: transparent; border: none;")
        self.time_label.setAlignment(Qt.AlignRight)
        
        info_layout.addWidget(desc_label)
        info_layout.addWidget(self.time_label)
        layout.addLayout(info_layout)
        
        self._current_path = None

    def update_image(self, image_path):
        """Carga y muestra una imagen desde la ruta dada."""
        from PySide6.QtGui import QPixmap, QImage
        from PySide6.QtCore import QSize
        from datetime import datetime
        
        self.log_message.emit(f"[CAM] Cargando: {os.path.basename(image_path)}")
        # Leer bytes crudos para evitar cualquier cache de Qt
        try:
            with open(image_path, 'rb') as f:
                raw_data = f.read()
        except Exception as e:
            self.log_message.emit(f"[CAM] ERROR leyendo: {e}")
            return
        
        image = QImage()
        if image.loadFromData(raw_data):
            pixmap = QPixmap.fromImage(image)
            target_size = self.img_label.size()
            if target_size.width() < 10 or target_size.height() < 10:
                target_size = QSize(420, 300)
            scaled = pixmap.scaled(
                target_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.img_label.setPixmap(scaled)
            self._current_path = image_path
            now = datetime.now().strftime("%H:%M:%S")
            self.time_label.setText(f"📷 {now}")
            self.log_message.emit(f"[CAM] OK: {image.width()}x{image.height()} → {scaled.width()}x{scaled.height()}")
        else:
            self.log_message.emit(f"[CAM] ERROR decodificando: {os.path.basename(image_path)}")
    
    def clear_image(self):
        """Vuelve al estado de espera."""
        self.img_label.clear()
        self.img_label.setText("Waiting for image...")
        self.time_label.setText("")
        self._current_path = None

class LogConsole(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(styles.CAMERA_FRAME_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Area de texto (readonly)
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet(
            "background-color: #0d1117; color: #3fb950; "
            "font-family: 'Consolas', monospace; font-size: 11px; "
            "border: 1px solid #30363d; border-radius: 4px; padding: 4px;"
        )
        # Ocultar scrollbars hasta que sean necesarios, customizar color
        self.text_area.verticalScrollBar().setStyleSheet(
            "QScrollBar:vertical { background: #0d1117; width: 10px; }"
            "QScrollBar::handle:vertical { background: #30363d; border-radius: 5px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        )
        
        layout.addWidget(self.text_area)
        
        # Max lineas para no saturar memoria
        self.max_lines = 100
        self._lines_count = 0
        
    def append_log(self, text):
        """Añade una línea de texto cruda y hace auto-scroll si está activado."""
        if not text:
            return
            
        self._lines_count += 1
        # Limpiar si excedemos el límite (rendimiento)
        if self._lines_count > self.max_lines:
            doc = self.text_area.document()
            cursor = self.text_area.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            self._lines_count -= 1
            
        # Añadir texto sin formatos complejos (más rápido)
        self.text_area.append(text)
        
        # Scroll dinámico abajo
        scrollbar = self.text_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        self.text_area.clear()
        self._lines_count = 0