from dataclasses import dataclass

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