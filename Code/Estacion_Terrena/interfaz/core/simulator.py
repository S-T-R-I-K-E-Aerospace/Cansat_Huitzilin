import random
import math
from PySide6.QtCore import QObject, Signal, QTimer

class TelemetrySimulator(QObject):
    data_updated = Signal(dict)
    raw_data_received = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_step)
        self.elapsed_time = 0

    def start(self, update_interval_ms=100):
        self.timer.start(update_interval_ms)

    def stop(self):
        self.timer.stop()

    def simulate_step(self):
        self.elapsed_time += 1
        t = self.elapsed_time % 120
        altitude = max(0, -0.5 * (t - 80)**2 + 1310)
        velocity = abs(-(t - 80) + random.uniform(-5, 5))
        acceleration = random.uniform(0.8, 2.5)
        temperature = 20 - (altitude / 100) + random.uniform(-1, 1)
        pressure = 1013.25 * math.exp(-altitude / 8500)
        battery = max(0, 100 - self.elapsed_time / 10)
        heading = (self.elapsed_time * 1.5) % 360  # Rotación lenta simulada
        deployed = t > 80  # Despliegue después del apogeo
        # GPS simulado cerca de UAM Azcapotzalco con drift por viento
        base_lat = 19.5064
        base_lon = -99.1847
        latitude = base_lat + (self.elapsed_time * 0.00002) + random.uniform(-0.0001, 0.0001)
        longitude = base_lon + (self.elapsed_time * 0.00001) + random.uniform(-0.0001, 0.0001)
        data = {
            'altitude': altitude,
            'velocity': velocity,
            'acceleration': acceleration,
            'temperature': temperature,
            'pressure': pressure,
            'battery': battery,
            'heading': heading,
            'deployed': deployed,
            'latitude': latitude,
            'longitude': longitude,
        }
        
        # Generar string CSV para simular la entrada serial cruda (raw data logs)
        raw_csv = f"{altitude:.2f},{velocity:.2f},{acceleration:.2f},{temperature:.2f},{pressure:.2f},{battery:.1f},{heading:.1f},{int(deployed)},{latitude:.6f},{longitude:.6f}"
        
        self.raw_data_received.emit(raw_csv)
        self.data_updated.emit(data)