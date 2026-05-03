from collections.abc import Iterable

from summit_timer.protocol import DataAck


class RecordStore:
    """In-memory source of truth for records received from timers."""

    def __init__(self):
        self._records: dict[int, dict[int, DataAck]] = {}

    def add(self, record: DataAck) -> bool:
        device_records = self._records.setdefault(record.device_id, {})
        if record.record_number in device_records:
            return False

        device_records[record.record_number] = record
        return True

    def add_many(self, records: Iterable[DataAck]) -> list[DataAck]:
        return [record for record in records if self.add(record)]

    def records_for_device(self, device_id: int) -> list[DataAck]:
        return [
            record for _, record in sorted(self._records.get(device_id, {}).items())
        ]

    def all_records(self) -> list[DataAck]:
        records = []
        for device_id in sorted(self._records):
            records.extend(self.records_for_device(device_id))
        return records

    def next_missing_record_number(self, device_id: int) -> int:
        record_numbers = self._records.get(device_id, {})
        record_number = 1
        while record_number in record_numbers:
            record_number += 1
        return record_number

    def latest_record_number(self, device_id: int) -> int | None:
        record_numbers = self._records.get(device_id, {})
        if not record_numbers:
            return None
        return max(record_numbers)

    def count(self, device_id: int) -> int:
        return len(self._records.get(device_id, {}))
