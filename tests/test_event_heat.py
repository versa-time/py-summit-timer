from summit_timer import protocol as proto


def test_set_event_and_heat_round_trips():
    packet = proto.SetEventAndHeat(device_id=1, event_number=26, heat_number=20)

    assert proto.Packet.from_string(str(packet)) == packet
