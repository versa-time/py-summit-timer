import datetime

from summit_timer import protocol as proto
from summit_timer.client import SummitTimerClient


class FakeTransport:
    def __init__(
        self,
        connected_devices: set[int] | None = None,
        responses: list[proto.Packet | None] | None = None,
    ):
        if connected_devices is None:
            connected_devices = set()
        self.connected_devices = connected_devices
        self.responses = responses or []
        self.sent_packets = []
        self.cleared = 0

    def clear_input_buffer(self):
        self.cleared += 1

    def send(self, packet):
        self.sent_packets.append(packet)

    def read_packet(self, timeout=None):
        if self.responses:
            return self.responses.pop(0)

        packet = self.sent_packets[-1]
        if (
            isinstance(packet, proto.GetData)
            and packet.device_id in self.connected_devices
        ):
            return proto.Ack(packet.device_id)
        return None


def test_discover_devices_returns_acknowledged_ids():
    client = SummitTimerClient(FakeTransport({7, 42}), device_id=0)

    discovered = client.discover_devices(1, 50, timeout=0.01, quiet_delay=0)

    assert discovered == [7, 42]


def test_ping_host_clears_stale_input_before_request():
    transport = FakeTransport({3})
    client = SummitTimerClient(transport, device_id=0)

    assert client.ping_host(3, timeout=0.01) is True
    assert transport.cleared == 1
    assert transport.sent_packets == [proto.GetData(3, 1)]


def test_ping_host_detects_device_that_returns_data():
    record = proto.DataAck(
        3,
        1,
        20,
        5,
        1,
        "b",
        "45",
        datetime.datetime.strptime("01:02:03.4", "%H:%M:%S.%f").time(),
    )
    transport = FakeTransport(responses=[record])
    client = SummitTimerClient(transport, device_id=0)

    assert client.ping_host(3, timeout=0.01) is True


def test_get_data_reads_records_until_ack():
    first_record = proto.DataAck(
        1,
        1,
        20,
        5,
        1,
        "b",
        "45",
        datetime.datetime.strptime("01:02:03.4", "%H:%M:%S.%f").time(),
    )
    second_record = proto.DataAck(
        1,
        2,
        20,
        5,
        1,
        "s",
        "",
        datetime.datetime.strptime("01:02:04.5", "%H:%M:%S.%f").time(),
    )
    responses = [
        first_record,
        second_record,
        proto.Ack(1),
    ]
    transport = FakeTransport(responses=responses)
    client = SummitTimerClient(transport, device_id=0)

    records = client.get_data(1, 1, timeout=0.01)

    assert records == [first_record, second_record]
    assert transport.sent_packets == [proto.GetData(1, 1)]


def test_discover_devices_silences_bus_before_pinging():
    transport = FakeTransport({4, 8})
    client = SummitTimerClient(transport, device_id=0)

    discovered = client.discover_devices(1, 10, timeout=0.01, quiet_delay=0)

    assert discovered == [4, 8]
    assert transport.sent_packets[0] == proto.GiveToken(0)
    getdata_packets = [
        p for p in transport.sent_packets if isinstance(p, proto.GetData)
    ]
    assert len(getdata_packets) == 10
    givetoken_zero = [
        p
        for p in transport.sent_packets
        if isinstance(p, proto.GiveToken) and p.device_id == 0
    ]
    assert len(givetoken_zero) == 11
    assert transport.cleared == 1 + 10 * 2


def test_poll_device_silences_bus_before_requesting_records():
    transport = FakeTransport(responses=[proto.Ack(2)])
    client = SummitTimerClient(transport, device_id=0)

    assert client.poll_device(2, 3, timeout=0.01, quiet_delay=0) == []
    assert transport.sent_packets == [proto.GiveToken(0), proto.GetData(2, 3)]
    assert transport.cleared == 1
