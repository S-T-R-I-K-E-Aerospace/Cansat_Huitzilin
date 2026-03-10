# main.py
import sys
from PySide6.QtWidgets import QApplication
from window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    app.setApplicationName("S.T.R.I.K.E Aerospace Mission Control")
    app.setApplicationVersion("1.0.1")
    app.setOrganizationName("S.T.R.I.K.E Aerospace")
    
    print("=" * 70)
    print("S.T.R.I.K.E Aerospace - Mission Control v1.0.1")
    print("Aplicación modular iniciada exitosamente")
    print("=" * 70)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()  