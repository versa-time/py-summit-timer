from PySide6.QtWidgets import QWidget, QVBoxLayout
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
        layout.addWidget(self.serial_manager)
        layout.addWidget(TimerManager(self.transport))
        layout.addWidget(DataWriter())

