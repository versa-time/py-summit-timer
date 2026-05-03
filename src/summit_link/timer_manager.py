from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QSize, QTimer

from summit_link.data_writer import DataWriter
from summit_timer.client import SummitTimerClient
from summit_timer.record_store import RecordStore
from summit_timer.transport import Transport

DISCOVER_MIN_DEVICE_ID = 1
DISCOVER_MAX_DEVICE_ID = 20
DISCOVER_TIMEOUT_SECONDS = 0.2
POLL_TIMEOUT_SECONDS = 0.1
POLL_QUIET_DELAY_SECONDS = 0.05


class TimerWidget(QWidget):
    def __init__(self, transport: Transport):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)
        self.device_label = QLabel("Device Num")
        self.device_num_input = QSpinBox()
        self.latest_received_label = QLabel("Seen Recently:")
        self.latest_received_label_value = QLabel("No")
        self.device_num_input.setReadOnly(True)
        layout.addWidget(self.device_label)
        layout.addWidget(self.device_num_input)
        layout.addWidget(self.latest_received_label)
        layout.addWidget(self.latest_received_label_value)

    @property
    def device_id(self) -> int:
        return self.device_num_input.value()

    def update_record_state(self, latest_record: int | None, record_count: int):
        if latest_record is None:
            self.latest_received_label_value.setText("No records")
        else:
            self.latest_received_label_value.setText(
                f"{record_count} records, latest #{latest_record}"
            )


class TimerManager(QGroupBox):
    def __init__(self, transport: Transport, data_writer: DataWriter | None = None):
        super().__init__()
        self.transport = transport
        self.data_writer = data_writer
        self.record_store = RecordStore()
        self.poll_index = 0
        self.setTitle("Timer Configuration")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.timer_widgets: list[TimerWidget] = []

        toolbar_layout = QHBoxLayout()
        self.discover_devices_button = QPushButton("Discover Devices")
        self.discover_devices_button.clicked.connect(self.discover_devices)
        self.auto_poll_button = QPushButton("Start Polling")
        self.auto_poll_button.setCheckable(True)
        self.auto_poll_button.toggled.connect(self.set_polling_enabled)
        self.connection_status_label = QLabel("Disconnected")
        toolbar_layout.addWidget(self.discover_devices_button)
        toolbar_layout.addWidget(self.auto_poll_button)
        toolbar_layout.addWidget(self.connection_status_label)
        layout.addLayout(toolbar_layout)
        self.timer_list = QVBoxLayout()
        self.timer_list_scroll_area = QScrollArea()
        self.timer_list_scroll_area.setWidgetResizable(True)
        self.timer_list_widget = QWidget()
        self.timer_list_widget.setLayout(self.timer_list)
        self.timer_list_scroll_area.setWidget(self.timer_list_widget)
        layout.addWidget(self.timer_list_scroll_area)
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(10)
        self.poll_timer.timeout.connect(self.poll_next_device)
        self.set_connection_state(False)

    def add_timer(self, device_id: int):
        timer_widget = TimerWidget(self.transport)
        timer_widget.device_num_input.setValue(device_id)
        self.timer_list.addWidget(timer_widget)
        self.timer_widgets.append(timer_widget)

    def clear_timer_list(self):
        while self.timer_list.count():
            child = self.timer_list.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
        self.timer_widgets.clear()
        self.poll_index = 0

    def set_connection_state(self, connected: bool, port: str = ""):
        self.discover_devices_button.setEnabled(connected)
        self.auto_poll_button.setEnabled(connected)
        if connected:
            self.connection_status_label.setText(f"Connected: {port}")
        else:
            self.set_polling_enabled(False)
            self.auto_poll_button.setChecked(False)
            self.connection_status_label.setText("Disconnected")
            self.clear_timer_list()

    def discover_devices(self):
        self.connection_status_label.setText("Discovering devices...")
        QApplication.processEvents()

        client = SummitTimerClient(self.transport, device_id=0)
        device_ids = client.discover_devices(
            start_device_id=DISCOVER_MIN_DEVICE_ID,
            end_device_id=DISCOVER_MAX_DEVICE_ID,
            timeout=DISCOVER_TIMEOUT_SECONDS,
        )

        self.clear_timer_list()
        self.record_store = RecordStore()
        for device_id in device_ids:
            self.add_timer(device_id)

        if device_ids:
            self.connection_status_label.setText(
                f"Discovered {len(device_ids)} device(s)"
            )
        else:
            self.connection_status_label.setText("No devices discovered")

    def set_polling_enabled(self, enabled: bool):
        if enabled:
            if not self.timer_widgets:
                self.auto_poll_button.setChecked(False)
                self.connection_status_label.setText("Discover devices before polling")
                return
            if (
                self.data_writer is not None
                and not self.data_writer.has_file_selected()
            ):
                self.auto_poll_button.setChecked(False)
                self.connection_status_label.setText(
                    "Select an Excel file before polling"
                )
                return

            self.auto_poll_button.setText("Stop Polling")
            self.poll_timer.start()
        else:
            self.poll_timer.stop()
            self.auto_poll_button.setText("Start Polling")

    def poll_next_device(self):
        if not self.timer_widgets:
            self.set_polling_enabled(False)
            return

        timer_widget = self.timer_widgets[self.poll_index % len(self.timer_widgets)]
        self.poll_index += 1
        device_id = timer_widget.device_id
        next_record = self.record_store.next_missing_record_number(device_id)

        client = SummitTimerClient(self.transport, device_id=0)
        try:
            records = client.poll_device(
                device_id,
                next_record,
                timeout=POLL_TIMEOUT_SECONDS,
                quiet_delay=POLL_QUIET_DELAY_SECONDS,
            )
        except Exception as exc:
            self.auto_poll_button.setChecked(False)
            self.connection_status_label.setText(f"Polling stopped: {exc}")
            return
        new_records = self.record_store.add_many(records)

        if self.data_writer is not None and new_records:
            try:
                writer = self.data_writer.get_writer()
                if writer is None:
                    self.auto_poll_button.setChecked(False)
                    self.connection_status_label.setText(
                        "Select an Excel file before polling"
                    )
                    return
                writer.append_records(new_records)
            except Exception as exc:
                self.auto_poll_button.setChecked(False)
                self.connection_status_label.setText(f"Excel write failed: {exc}")
                return

        latest_record = self.record_store.latest_record_number(device_id)
        timer_widget.update_record_state(
            latest_record,
            self.record_store.count(device_id),
        )
        self.connection_status_label.setText(
            f"Polling device {device_id}, next record #{self.record_store.next_missing_record_number(device_id)}"
        )

    def minimumSizeHint(self):
        return QSize(600, 200)
