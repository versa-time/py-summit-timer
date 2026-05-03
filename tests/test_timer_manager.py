import datetime
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from summit_link.timer_manager import TimerManager
from summit_timer.protocol import DataAck


def ensure_app():
    return QApplication.instance() or QApplication([])


def make_record(record_number: int) -> DataAck:
    return DataAck(
        device_id=1,
        record_number=record_number,
        event_number=20,
        heat_number=5,
        channel=1,
        record_type="b",
        user_string="45",
        time=datetime.datetime.strptime("01:02:03.4", "%H:%M:%S.%f").time(),
    )


def test_timer_manager_keeps_excel_records_pending_after_write_failure():
    ensure_app()
    writer = FlakyWriter()
    manager = TimerManager(object(), FakeDataWriter(writer))
    manager.pending_excel_records = [make_record(1)]

    assert not manager.write_pending_excel_records()

    assert [record.record_number for record in manager.pending_excel_records] == [1]
    assert "will retry" in manager.connection_status_label.text()

    assert manager.write_pending_excel_records()

    assert manager.pending_excel_records == []
    assert [record.record_number for record in writer.written] == [1]


class FakeDataWriter:
    def __init__(self, writer):
        self.writer = writer

    def get_writer(self):
        return self.writer


class FlakyWriter:
    def __init__(self):
        self.should_fail = True
        self.written = []

    def append_records(self, records):
        if self.should_fail:
            self.should_fail = False
            raise RuntimeError("Excel is busy")

        self.written.extend(records)
        return records
