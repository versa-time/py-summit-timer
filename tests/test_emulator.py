from summit_timer.client import SummitTimerClient
from summit_timer.emulator import SummitEmulator
from summit_timer.protocol import Ack, DataAck, GetData, GiveToken
from summit_timer.transport import EMULATOR_PORT, Transport


def test_emulator_acks_known_devices_only():
    emulator = SummitEmulator(device_ids=[4], initial_records=0)

    assert emulator.handle(GiveToken(4)) == [Ack(4)]
    assert emulator.handle(GiveToken(5)) == []
    assert emulator.handle(GiveToken(0)) == []


def test_emulator_returns_records_from_requested_row_then_ack():
    emulator = SummitEmulator(device_ids=[1], initial_records=3, record_interval=0)

    responses = emulator.handle(GetData(1, 2))

    assert [response.record_number for response in responses[:-1]] == [2, 3]
    assert responses[-1] == Ack(1)


def test_transport_can_use_emulator_port():
    with Transport(EMULATOR_PORT, timeout=0) as transport:
        client = SummitTimerClient(transport, device_id=0)

        assert client.ping_host(1, timeout=0) is True
        records = client.poll_device(1, 1, timeout=0, quiet_delay=0)

    assert records
    assert all(isinstance(record, DataAck) for record in records)
    assert [record.record_number for record in records] == [1, 2, 3]
