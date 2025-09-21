from src.summit_timer import protocol as proto


def test_crc():
    assert proto.GetData(1, 1).to_string() == "{TK 1 1}c12b"
    assert proto.Packet.from_string("{TK 1 1}c12b") == proto.GetData(1, 1)