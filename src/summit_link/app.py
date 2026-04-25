from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from .timer_manager import TimerManager
from .serial_manager import SerialManager
from importlib.metadata import version
from ..summit_timer.transport import Transport
from .data_writer import DataWriter

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Summit Link App - v{version('py-summit-timer')}")  # name and version
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Add widgets
        self.transport = Transport("")
        self.serial_manager = SerialManager()
        self.timer_manager = TimerManager(self.transport)
        layout.addWidget(self.serial_manager)
        layout.addWidget(self.timer_manager)
        layout.addWidget(DataWriter())

        self.serial_manager.connect_signal.connect(self.connect_transport)
        self.serial_manager.disconnect_signal.connect(self.disconnect_transport)

    def connect_transport(self, port: str):
        try:
            self.transport.close()
            self.transport.set_port(port)
            self.transport.open()
        except Exception as exc:
            self.serial_manager.set_connected(False)
            self.timer_manager.set_connection_state(False)
            QMessageBox.critical(self, "Connection Failed", str(exc))
            return

        self.serial_manager.set_connected(True)
        self.timer_manager.set_connection_state(True, port)

    def disconnect_transport(self):
        self.transport.close()
        self.serial_manager.set_connected(False)
        self.timer_manager.set_connection_state(False)
