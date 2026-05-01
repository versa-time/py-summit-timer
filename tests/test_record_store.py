import datetime

from summit_timer.protocol import DataAck
from summit_timer.record_store import RecordStore


def make_record(device_id: int, record_number: int) -> DataAck:
    return DataAck(
        device_id=device_id,
        record_number=record_number,
        event_number=20,
        heat_number=5,
        channel=1,
        record_type="b",
        user_string="45",
        time=datetime.datetime.strptime("01:02:03.4", "%H:%M:%S.%f").time(),
    )


def test_store_ignores_duplicate_device_record_pairs():
    store = RecordStore()
    record = make_record(1, 1)

    assert store.add(record) is True
    assert store.add(record) is False

    assert store.records_for_device(1) == [record]


def test_store_requests_first_gap_before_new_tail():
    store = RecordStore()
    store.add(make_record(1, 1))
    store.add(make_record(1, 2))
    store.add(make_record(1, 4))

    assert store.next_missing_record_number(1) == 3


def test_store_requests_next_tail_when_there_are_no_gaps():
    store = RecordStore()
    store.add(make_record(1, 1))
    store.add(make_record(1, 2))

    assert store.next_missing_record_number(1) == 3
    assert store.latest_record_number(1) == 2
    assert store.count(1) == 2
