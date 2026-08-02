import datetime
import time
from collections import deque

from summit_timer.protocol import Ack, DataAck, GetData, GiveToken, Packet


class SummitEmulator:
    """Small protocol emulator for local GUI and client testing."""

    def __init__(
        self,
        device_ids: list[int] | None = None,
        initial_records: int = 3,
        max_records: int = 25,
        record_interval: float = 2.0,
    ):
        if device_ids is None:
            device_ids = [1, 2, 4, 5]

        self.device_ids = set(device_ids)
        self.max_records = max_records
        self.record_interval = record_interval
        self.started_at = time.monotonic()
        self.records: dict[int, list[DataAck]] = {
            device_id: [
                self._make_record(device_id, record_number)
                for record_number in range(1, initial_records + 1)
            ]
            for device_id in device_ids
        }

    def handle(self, packet: Packet | None) -> list[Packet]:
        if packet is None:
            return []

        self._generate_due_records()

        if isinstance(packet, GiveToken):
            if packet.device_id in self.device_ids:
                return [Ack(packet.device_id)]
            return []

        if isinstance(packet, GetData):
            if packet.device_id not in self.device_ids:
                return []

            records = [
                record
                for record in self.records[packet.device_id]
                if record.record_number >= packet.row_number
            ]
            return [*records, Ack(packet.device_id)]

        return []

    def _generate_due_records(self):
        if self.record_interval <= 0:
            return

        desired_count = int((time.monotonic() - self.started_at) / self.record_interval)
        for device_id in self.device_ids:
            records = self.records[device_id]
            target_count = min(self.max_records, max(len(records), desired_count))
            while len(records) < target_count:
                records.append(self._make_record(device_id, len(records) + 1))

    def _make_record(self, device_id: int, record_number: int) -> DataAck:
        base_time = datetime.datetime.strptime("09:00:00.0", "%H:%M:%S.%f")
        record_time = base_time + datetime.timedelta(
            seconds=(device_id * 10) + record_number
        )
        return DataAck(
            device_id=device_id,
            record_number=record_number,
            event_number=1,
            heat_number=1,
            channel=device_id,
            record_type="b" if record_number % 2 else "s",
            user_string=str(1000 + (device_id * 100) + record_number),
            time=record_time.time(),
        )


class EmulatorSerial:
    """pyserial-like connection backed by SummitEmulator."""

    def __init__(self, timeout: float = 1.0, emulator: SummitEmulator | None = None):
        self.timeout = timeout
        self.emulator = emulator or SummitEmulator()
        self.is_open = True
        self._lines: deque[bytes] = deque()

    @property
    def in_waiting(self) -> int:
        return len(self._lines)

    def close(self):
        self.is_open = False

    def reset_input_buffer(self):
        self._lines.clear()

    def write(self, data: bytes):
        if not self.is_open:
            raise ConnectionError("Emulator connection is closed.")

        line = data.decode(encoding="ascii").strip()
        packet = Packet.from_string(line)
        for response in self.emulator.handle(packet):
            self._lines.append(f"{response}\r\n".encode())

    def readline(self) -> bytes:
        if self._lines:
            return self._lines.popleft()

        if self.timeout:
            time.sleep(self.timeout)
        return b""
