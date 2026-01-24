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
        self.transport.send(proto.GiveToken(device_id))
        response = self.transport.receive()
        return isinstance(response, proto.Ack) and response.device_id == device_id

    def set_event_and_heat(
        self, device_id: int, event_number: int, heat_number: int
    ) -> bool:
        """Set the event and heat number on a device."""
        self.transport.send(proto.SetEventAndHeat(device_id, event_number, heat_number))
        response = self.transport.receive()
        return isinstance(response, proto.Ack) and response.device_id == device_id

    def get_data(self, device_id: int, row_number: int) -> list[proto.DataAck] | None:
        """Get data from a device."""
        self.transport.send(proto.GetData(device_id, row_number))
        response = self.transport.receive()
        if isinstance(response, proto.DataAck) and response.device_id == device_id:
            return [response]
        return None
