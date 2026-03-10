# ui/styles.py — Modern Glassmorphism Theme

MAIN_WINDOW_STYLE = """
    QMainWindow { 
        background-color: #080c14;
    }
"""

DATA_DISPLAY_STYLE = """
    DataDisplay {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(22, 27, 34, 240),
            stop:1 rgba(13, 17, 23, 250));
        border: 1px solid rgba(56, 68, 82, 0.6);
        border-radius: 10px;
    }
    DataDisplay:hover {
        border: 1px solid rgba(88, 166, 255, 0.3);
    }
"""

METAL_PANEL_STYLE = """
    MetalPanel {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(22, 27, 34, 230),
            stop:1 rgba(13, 17, 23, 245));
        border: 1px solid rgba(48, 54, 61, 0.7);
        border-top: 1px solid rgba(88, 166, 255, 0.15);
        border-radius: 14px;
    }
"""

HEADER_STYLE = """
    QFrame {
        background-color: transparent;
        border: none;
        border-bottom: 1px solid rgba(48, 54, 61, 0.5);
        border-radius: 0px;
    }
"""

CAMERA_FRAME_STYLE = """
    QFrame {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(8, 12, 20, 255),
            stop:1 rgba(13, 17, 23, 255));
        border: 1px solid rgba(48, 54, 61, 0.6);
        border-radius: 10px;
    }
"""

# Estilo para títulos de paneles
PANEL_TITLE_STYLE = """
    color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #58a6ff, stop:1 #79c0ff);
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 3px;
    background: transparent;
    border: none;
    padding: 4px 0px;
"""

# Estilo para labels de datos
DATA_LABEL_STYLE = "color: #6e7681; font-size: 10px; font-weight: 600; letter-spacing: 1px; background: transparent; border: none;"

# Estilo para valores de datos
DATA_VALUE_STYLE = "color: #e6edf3; font-size: 28px; font-weight: bold; font-family: 'Consolas', 'Cascadia Code', monospace; background: transparent; border: none;"

# Botones modernos
BUTTON_PRIMARY_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #238636, stop:1 #1a6b2c);
        color: #ffffff;
        border: 1px solid rgba(46, 160, 67, 0.5);
        border-radius: 8px;
        padding: 10px;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #2ea043, stop:1 #238636);
        border: 1px solid rgba(46, 160, 67, 0.8);
    }
    QPushButton:pressed {
        background: #1a6b2c;
    }
"""

BUTTON_SECONDARY_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(33, 38, 45, 230), stop:1 rgba(22, 27, 34, 240));
        color: #c9d1d9;
        border: 1px solid rgba(48, 54, 61, 0.7);
        border-radius: 8px;
        padding: 10px;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(48, 54, 61, 230), stop:1 rgba(33, 38, 45, 240));
        border: 1px solid rgba(139, 148, 158, 0.4);
    }
    QPushButton:pressed {
        background: #161b22;
    }
"""

BUTTON_DANGER_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(33, 38, 45, 230), stop:1 rgba(22, 27, 34, 240));
        color: #ff7b72;
        border: 1px solid rgba(48, 54, 61, 0.7);
        border-radius: 8px;
        padding: 10px;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(48, 54, 61, 230), stop:1 rgba(33, 38, 45, 240));
        border: 1px solid rgba(255, 123, 114, 0.5);
    }
    QPushButton:pressed {
        background: #161b22;
    }
"""

BUTTON_DISABLED_STYLE = """
    QPushButton {
        background: rgba(22, 27, 34, 200);
        color: #484f58;
        border: 1px solid rgba(33, 38, 45, 0.5);
        border-radius: 8px;
        padding: 10px;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
    }
"""

BUTTON_ACTIVE_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #e3b341, stop:1 #c99b2e);
        color: #1a1a1a;
        border: 1px solid rgba(227, 179, 65, 0.7);
        border-radius: 8px;
        padding: 10px;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f0c060, stop:1 #e3b341);
    }
    QPushButton:pressed {
        background: #c99b2e;
    }
"""

COMBOBOX_STYLE = """
    QComboBox {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(13, 17, 23, 240), stop:1 rgba(8, 12, 20, 250));
        color: #c9d1d9;
        border: 1px solid rgba(48, 54, 61, 0.7);
        border-radius: 6px;
        padding: 6px 10px;
        font-weight: bold;
        font-size: 11px;
    }
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView {
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
        selection-background-color: #1f6feb;
    }
"""

MINI_GRAPH_STYLE = "border: 1px solid rgba(48, 54, 61, 0.5); border-radius: 6px;"