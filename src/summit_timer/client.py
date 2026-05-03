from .transport import Transport
import summit_timer.protocol as proto
import time

MAX_DEVICES = 16
DISCOVERY_ROW_NUMBER = 1


class SummitTimerClient:
    def __init__(self, transport: Transport, device_id: int):
        self.transport = transport
        self.device_id = device_id

    def ping_host(self, device_id: int, timeout: float = 0.1) -> bool:
        """Ping a device to see if it is connected."""
        self.transport.clear_input_buffer()
        self.transport.send(proto.GetData(device_id, DISCOVERY_ROW_NUMBER))
        response = self.transport.read_packet(timeout=timeout)
        return (
            isinstance(response, proto.Ack | proto.DataAck)
            and response.device_id == device_id
        )

    def discover_devices(
        self, start_device_id: int = 1, end_device_id: int = 255, timeout: float = 0.1
    ) -> list[int]:
        """Discover connected devices by requesting an ACK from each device ID."""
        discovered_devices = []
        for device_id in range(start_device_id, end_device_id + 1):
            if self.ping_host(device_id, timeout=timeout):
                discovered_devices.append(device_id)
        self.transport.clear_input_buffer()
        return discovered_devices

    def set_event_and_heat(
        self, device_id: int, event_number: int, heat_number: int
    ) -> bool:
        """Set the event and heat number on a device."""
        self.transport.send(proto.SetEventAndHeat(device_id, event_number, heat_number))
        response = self.transport.read_packet()
        return isinstance(response, proto.Ack) and response.device_id == device_id

    def stop_all_devices(self):
        """Tell every timer on the bus to stop talking."""
        self.transport.send(proto.GiveToken(0))

    def get_data(
        self, device_id: int, row_number: int, timeout: float = 0.2
    ) -> list[proto.DataAck]:
        """Get all records a device sends for one token request."""
        self.transport.send(proto.GetData(device_id, row_number))
        records = []

        while True:
            response = self.transport.read_packet(timeout=timeout)
            if response is None:
                return records

            if isinstance(response, proto.Ack) and response.device_id == device_id:
                return records

            if isinstance(response, proto.DataAck) and response.device_id == device_id:
                records.append(response)

    def poll_device(
        self,
        device_id: int,
        row_number: int,
        timeout: float = 0.2,
        quiet_delay: float = 0.05,
    ) -> list[proto.DataAck]:
        """Silence the bus, then request records from one device."""
        self.transport.clear_input_buffer()
        self.stop_all_devices()
        if quiet_delay > 0:
            time.sleep(quiet_delay)
        return self.get_data(device_id, row_number, timeout=timeout)
