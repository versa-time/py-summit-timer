from dataclasses import dataclass
from typing import Generator
        
class Packet:
    @staticmethod
    def from_parts(parts: list[str]) -> 'Packet | None':
        if len(parts) >= 1:
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
                            time=parts[7],
                        )
                    except ValueError:
                        pass
        return None


@dataclass
class Reset(Packet):
    pass

@dataclass
class DisableReset(Packet):
    pass

@dataclass
class Synch(Packet):
    hour: int
    minute: int
    second: float

@dataclass
class SynchOffset(Packet):
    hour: int
    minute: int
    second: float

@dataclass
class GiveToken(Packet):
    device_id: int

@dataclass
class GetData(Packet):
    device_id: int
    row_number: int

@dataclass
class SetEventAndHeat(Packet):
    device_id: int
    event_number: int
    heat_number: int

@dataclass
class Ack(Packet):
    device_id: int

@dataclass
class DataAck(Packet):
    device_id: int
    record_number: int
    event_number: int
    heat_number: int
    channel: int
    record_type: str
    user_string: str
    time: str