from dataclasses import dataclass
from abc import abstractmethod
from crc import Calculator, Configuration
import datetime

CRC_CONFIG = Configuration(
    width=16,
    polynomial=0x8005,
    init_value=0x0000,
    final_xor_value=0x0000,
    reverse_input=True,
    reverse_output=True,
)
CRC_CALCULATOR = Calculator(CRC_CONFIG)


def validate_crc(data: str, crc: str) -> bool:
    """Validate the CRC format."""
    try:
        crc_int = int(crc, 16)
        return CRC_CALCULATOR.verify(data.encode(), crc_int)
    except ValueError:
        return False


def data_from_string(data: str) -> list[str] | None:
    """Strings follow the format:
    {data}CRC
    """
    # Does the packet fit the format?
    if data.startswith("{"):
        end = data.find("}")
        if end != -1:
            content = data[1:end]
            crc = data[end + 1 :]
            if validate_crc(content, crc.strip()):
                # Data packets are tab-separated
                if "\t" in content:
                    return content.split("\t")
                # Command and Response packets are space-separated
                return content.split(" ")

    return None


def wrap_payload(payload: str) -> str:
    """Wrap a payload in the CRC format."""
    crc = CRC_CALCULATOR.checksum(payload.encode())
    return f"{{{payload}}}{crc:04x}"


class Packet:
    @staticmethod
    def from_string(data: str) -> "Packet | None":
        parts = data_from_string(data)
        print(parts)
        if parts:
            match parts[0]:
                case "RS":  # Reset / Disable Reset
                    if len(parts) == 1:
                        return Reset()
                    elif len(parts) == 2 and parts[1] == "x":
                        return DisableReset()
                case "SY":  # Synchronize
                    timestamp = parts[1]
                    timestamp_split = timestamp.split(":")
                    return Synch(
                        hour=int(timestamp_split[0]),
                        minute=int(timestamp_split[1]),
                        second=float(timestamp_split[2]),
                    )
                case "SYO":  # Synchronize Offset
                    timestamp = parts[1]
                    timestamp_split = timestamp.split(":")
                    return SynchOffset(
                        hour=int(timestamp_split[0]),
                        minute=int(timestamp_split[1]),
                        second=float(timestamp_split[2]),
                    )
                case "TK":  # Token
                    if len(parts) == 3:
                        return GetData(
                            device_id=int(parts[1]), row_number=int(parts[2])
                        )
                    elif len(parts) == 2:
                        return GiveToken(device_id=int(parts[1]))
                case "EV":  # Event and Heat
                    return SetEventAndHeat(
                        device_id=int(parts[1]),
                        event_number=int(parts[2]),
                        heat_number=int(parts[3]),
                    )
                case "AK":  # Acknowledge
                    return Ack(device_id=int(parts[1]))
                case _:
                    try:
                        int(parts[0])  # This is a data packet
                        return DataAck(
                            device_id=int(parts[0]),
                            record_number=int(parts[1]),
                            event_number=int(parts[2]),
                            heat_number=int(parts[3]),
                            channel=int(parts[4]),
                            record_type=parts[5],
                            user_string=parts[6],
                            time=datetime.datetime.strptime(
                                parts[7], "%H:%M:%S.%f"
                            ).time(),
                        )
                    except ValueError:
                        pass
        return None

    @abstractmethod
    def _to_payload(self) -> str:
        raise NotImplementedError()

    def to_string(self) -> str:
        return wrap_payload(self._to_payload())


@dataclass
class Reset(Packet):
    def _to_payload(self) -> str:
        return "RS"


@dataclass
class DisableReset(Packet):
    def _to_payload(self) -> str:
        return "RS x"


@dataclass
class Synch(Packet):
    hour: int
    minute: int
    second: float

    def _to_payload(self) -> str:
        return f"SY {self.hour}:{self.minute}:{self.second:.1f}"


@dataclass
class SynchOffset(Packet):
    hour: int
    minute: int
    second: float

    def _to_payload(self) -> str:
        return f"SYO {self.hour}:{self.minute}:{self.second:.1f}"


@dataclass
class GiveToken(Packet):
    device_id: int

    def _to_payload(self) -> str:
        return f"TK {self.device_id}"


@dataclass
class GetData(Packet):
    device_id: int
    row_number: int

    def _to_payload(self) -> str:
        return f"TK {self.device_id} {self.row_number}"


@dataclass
class SetEventAndHeat(Packet):
    device_id: int
    event_number: int
    heat_number: int

    def _to_payload(self) -> str:
        return f"EV {self.device_id} {self.event_number} {self.heat_number}"


@dataclass
class Ack(Packet):
    device_id: int

    def _to_payload(self) -> str:
        return f"AK {self.device_id}"


@dataclass
class DataAck(Packet):
    device_id: int
    record_number: int
    event_number: int
    heat_number: int
    channel: int
    record_type: str
    user_string: str
    time: datetime.time

    def _to_payload(self) -> str:
        return f"{self.device_id}\t{self.record_number}\t{self.event_number}\t{self.heat_number}\t{self.channel}\t{self.record_type}\t{self.user_string}\t{self.time.strftime('%H:%M:%S') + f'.{int(self.time.microsecond / 100000)}'}"
