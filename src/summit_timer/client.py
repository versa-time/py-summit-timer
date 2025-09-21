from .transport import Transport
import summit_timer.protocol as proto
import datetime

MAX_DEVICES = 16


class SummitTimerClient:
    def __init__(self, transport: Transport, device_id: int):
        self.transport = transport
        self.device_id = device_id

    def ping_host(self, device_id: int) -> bool:
        """Ping a device to see if it is connected."""
        if device_id < 1 or device_id > MAX_DEVICES:
            raise ValueError("Invalid device ID")
        self.transport.send(proto.GiveToken(device_id))
        undecoded = self.transport.receive()
        response = proto.Packet.from_string(undecoded)
        return isinstance(response, proto.Ack) and response.device_id == device_id

    def set_event_and_heat(
        self, device_id: int, event_number: int, heat_number: int
    ) -> bool:
        """Set the event and heat number on a device."""
        if device_id not in self.connected_hosts:
            raise ValueError("Invalid device ID")
        self.transport.send(proto.SetEventAndHeat(device_id, event_number, heat_number))
        undecoded = self.transport.receive()
        response = proto.Packet.from_string(undecoded)
        return isinstance(response, proto.Ack) and response.device_id == device_id

    def get_data(self, device_id: int, row_number: int) -> list[proto.DataAck] | None:
        """Get data from a device."""
        if device_id not in self.connected_hosts:
            raise ValueError("Invalid device ID")
        self.transport.send(proto.GetData(device_id, row_number))
        undecoded = self.transport.receive()
        response = proto.Packet.from_string(undecoded)
        if isinstance(response, proto.DataAck) and response.device_id == device_id:
            return [response]
        return None

    def synchronize_time_for_all_devices(
        self, time: datetime.time | None = None
    ) -> bool:
        """Synchronize the time on all devices.
        If no time is provided, the current system time is used.
        """
        if time is None:
            time = datetime.datetime.now().time()
        self.transport.send(proto.SynchOffset(time.hour, time.minute, time.second))
        undecoded = self.transport.receive()
        response = proto.Packet.from_string(undecoded)
        return isinstance(response, proto.Ack) and response.device_id == 0
