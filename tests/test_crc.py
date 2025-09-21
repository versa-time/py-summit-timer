from src.summit_timer import protocol as proto
import datetime


def test_crc_ack():
    assert proto.GetData(1, 1).to_string() == "{TK 1 1}c12b"
    assert proto.Packet.from_string("{TK 1 1}c12b") == proto.GetData(1, 1)
    assert proto.Packet.from_string("{TK 0}f279") == proto.GiveToken(0)


def test_crc_data():
    print(
        proto.DataAck(
            device_id=12,
            record_number=34,
            event_number=56,
            heat_number=78,
            channel=9,
            record_type="b",
            user_string="9999",
            time=datetime.datetime.strptime("12:34:56.7", "%H:%M:%S.%f").time(),
        ).to_string()
    )
    assert proto.Packet.from_string(
        "{12\t34\t56\t78\t9\tb\t9999\t12:34:56.7}4e72"
    ) == proto.DataAck(
        device_id=12,
        record_number=34,
        event_number=56,
        heat_number=78,
        channel=9,
        record_type="b",
        user_string="9999",
        time=datetime.datetime.strptime("12:34:56.7", "%H:%M:%S.%f").time(),
    )
