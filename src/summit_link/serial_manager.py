from serial.tools import list_ports
from PySide6.QtWidgets import QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox
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
        self.connect_button.clicked.connect(self.request_connect)

    def refresh_ports(self):
        current_port = self.port_combo.currentText()
        self.port_combo.clear()

        ports = sorted(list_ports.comports(), key=lambda port: port.device)
        available_ports = []
        for port in ports:
            # Only show usb or rs-232 ports
            if port.vid is not None or "RS-232" in port.description:
                available_ports.append(port.device)
                self.port_combo.addItem(port.device)

        has_ports = bool(available_ports)
        self.port_combo.setEnabled(has_ports)
        self.connect_button.setEnabled(has_ports)

        if current_port in available_ports:
            self.port_combo.setCurrentText(current_port)

    def request_connect(self):
        if not self.port_combo.currentText():
            return
        self.connect_signal.emit(self.port_combo.currentText())

    def request_disconnect(self):
        self.disconnect_signal.emit()

    def set_connected(self, connected: bool):
        try:
            self.connect_button.clicked.disconnect()
        except TypeError:
            pass
        if connected:
            self.connect_button.setText("Disconnect")
            self.connect_button.clicked.connect(self.request_disconnect)
        else:
            self.connect_button.setText("Connect")
            self.connect_button.clicked.connect(self.request_connect)
