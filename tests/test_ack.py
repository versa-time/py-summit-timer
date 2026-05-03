from summit_timer import protocol as proto


def test_ack_packet_round_trips():
    packet = proto.Ack(device_id=2)

    assert proto.Packet.from_string(str(packet)) == packet


def test_malformed_packets_return_none():
    assert proto.Packet.from_string(proto.wrap_payload("AK nope")) is None
    assert proto.Packet.from_string(proto.wrap_payload("1\t2\t3")) is None
