# core/serial_reader.py
import serial
import serial.tools.list_ports
import time
from PySide6.QtCore import QThread, Signal

class SerialReader(QThread):
    data_updated = Signal(dict)
    raw_data_received = Signal(str)
    connection_status = Signal(str, str)

    def __init__(self, port="", baudrate=115200, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.is_running = False
        self.serial_conn = None

    @staticmethod
    def get_available_ports():
        """Devuelve una lista con los nombres de los puertos disponibles (ej. COM3, /dev/ttyUSB0)"""
        return [port.device for port in serial.tools.list_ports.comports()]

    def run(self):
        self.is_running = True
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.connection_status.emit(f"CONNECTED: {self.port}", "#4caf50")
            
            while self.is_running:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.raw_data_received.emit(line)
                        self.parse_data(line)
                else:
                    time.sleep(0.01)
                    
        except serial.SerialException as e:
            self.connection_status.emit("PORT ERROR", "#ff5252")
            print(f"Error Serial: {e}")
            self.is_running = False
        finally:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
            self.connection_status.emit("DISCONNECTED", "#ff5252")

    def parse_data(self, line):
        try:
            parts = line.split(',')
            if len(parts) >= 6:
                data = {
                    'altitude':     float(parts[0]),
                    'velocity':     float(parts[1]),
                    'acceleration': float(parts[2]),
                    'temperature':  float(parts[3]),
                    'pressure':     float(parts[4]),
                    'battery':      float(parts[5]),
                    'heading':      float(parts[6]) if len(parts) >= 7 else 0.0,
                    'deployed':     int(parts[7]) == 1 if len(parts) >= 8 else False,
                    'latitude':     float(parts[8]) if len(parts) >= 9 else 0.0,
                    'longitude':    float(parts[9]) if len(parts) >= 10 else 0.0,
                }
                self.data_updated.emit(data)
        except ValueError:
            pass

    def stop(self):
        self.is_running = False
        self.wait()