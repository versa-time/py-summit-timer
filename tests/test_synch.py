from summit_timer import protocol as proto


def test_synch_packet_round_trips():
    packet = proto.Synch(hour=1, minute=2, second=3.4)

    assert proto.Packet.from_string(str(packet)) == packet


def test_synch_offset_packet_round_trips():
    packet = proto.SynchOffset(hour=1, minute=2, second=3.4)

    assert proto.Packet.from_string(str(packet)) == packet
