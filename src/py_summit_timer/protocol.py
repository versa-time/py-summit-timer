from dataclasses import dataclass
from typing import Generator
        
class Packet:
    @staticmethod
    def from_parts(parts: list[str]) -> 'Packet | None':
        if len(parts) < 1:
            return None
        match parts[0]:
            case "RS":  # Reset / Disable Reset
                pass
            case "SY":  # Synchronize
                pass
            case "SYO":  # Synchronize Offset
                pass
            case "TK":  # Token
                pass
            case "EV":  # Event and Heat
                pass
            case "AK":  # Acknowledge
                pass
            case _:
                try:
                    int(parts[0])  # This is a data packet
                except ValueError:
                    return None



@dataclass
class Command:
    crc: str

@dataclass
class Reset(Command):
    pass

@dataclass
class DisableReset(Command):
    pass

@dataclass
class Synch(Command):
    hour: int
    minute: int
    second: int
    millisecond: int

@dataclass
class SynchOffset(Command):
    hour: int
    minute: int
    second: int
    millisecond: int

@dataclass
class GiveToken(Command):
    device_id: int

@dataclass
class GetData(Command):
    device_id: int
    row_number: int

@dataclass
class SetEventAndHeat(Command):
    event_number: int
    heat_number: int

@dataclass
class Response:
    pass

@dataclass
class Ack(Response):
    crc: str

@dataclass
class DataAck(Response):
    device_id: int
    record_number: int
    event_number: int
    heat_number: int
    channel: int
    record_type: str
    user_string: str
    time: str