from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QListWidget, QListWidgetItem, QLCDNumber, QSpinBox, QLineEdit, QScrollArea
from PySide6.QtCore import QSize
from summit_timer.client import SummitTimerClient
from datetime import datetime
from ..summit_timer.transport import Transport
from ..summit_timer.client import SummitTimerClient


class TimerWidget(QWidget):
    def __init__(self, transport: Transport):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)
        self.device_label = QLabel("Device Num")
        self.device_num_input = QSpinBox()
        self.nickname_label = QLabel("Nickname")
        self.nickname_input = QLineEdit()
        self.nickname_input.setMinimumWidth(100)
        self.latest_received_label = QLabel("Seen Recently:")
        self.latest_received_label_value = QLabel("No")
        layout.addWidget(self.device_label)
        layout.addWidget(self.device_num_input)
        layout.addWidget(self.nickname_label)
        layout.addWidget(self.nickname_input)
        layout.addWidget(self.latest_received_label)
        layout.addWidget(self.latest_received_label_value)

class TimerManager(QGroupBox):
    def __init__(self, transport: Transport):
        super().__init__()
        self.transport = transport
        self.setTitle("Timer Configuration")
        layout = QVBoxLayout()
        self.setLayout(layout)

        toolbar_layout = QHBoxLayout()
        # add toolbar with buttons for add timer, sync timers
        self.add_timer_button = QPushButton("Add Timer")
        self.add_timer_button.clicked.connect(self.add_timer)
        self.sync_timers_button = QPushButton("Sync Timers")
        toolbar_layout.addWidget(self.add_timer_button)
        toolbar_layout.addWidget(self.sync_timers_button)
        layout.addLayout(toolbar_layout)
        self.timer_list = QVBoxLayout()
        self.timer_list_scroll_area = QScrollArea()
        self.timer_list_scroll_area.setWidgetResizable(True)
        self.timer_list_widget = QWidget()
        self.timer_list_widget.setLayout(self.timer_list)
        self.timer_list_scroll_area.setWidget(self.timer_list_widget)
        layout.addWidget(self.timer_list_scroll_area)

    def add_timer(self):
        timer_widget = TimerWidget(self.transport)
        self.timer_list.addWidget(timer_widget)

    def minimumSizeHint(self):
        return QSize(600, 200)