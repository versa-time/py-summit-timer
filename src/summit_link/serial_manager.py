from serial.tools import list_ports
from PySide6.QtWidgets import QWidget, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox
from PySide6.QtCore import Signal

class SerialManager(QGroupBox):

    connect_signal = Signal(str)
    disconnect_signal = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        sub_layout = QHBoxLayout()
        self.setLayout(layout)
        # get list of com ports
        # put them in a combo box
        self.setTitle("Select a Serial/USB Port")
        self.port_combo = QComboBox()
        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button = QPushButton("Connect")
        
        layout.addLayout(sub_layout)
        sub_layout.addWidget(self.port_combo)
        sub_layout.addWidget(self.refresh_button)
        sub_layout.addWidget(self.connect_button)
        # add a refresh button to regen the list
        # add a connect button that will emit which serial channel to use
        self.refresh_ports()
        self.connect_button.clicked.connect(self.connect)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = list_ports.comports()
        for port in ports:
            # Only show usb or rs-232 ports
            if port.vid is not None or "RS-232" in port.description:
                self.port_combo.addItem(port.device)
    
    def connect(self):
        self.connect_signal.emit(self.port_combo.currentText())
        self.connect_button.setText("Disconnect")
        self.connect_button.clicked.disconnect()
        self.connect_button.clicked.connect(self.disconnect)

    def disconnect(self):
        self.disconnect_signal.emit()
        self.connect_button.setText("Connect")
        self.connect_button.clicked.disconnect()
        self.connect_button.clicked.connect(self.connect)