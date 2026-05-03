import datetime

import pytest
from openpyxl import Workbook, load_workbook

from summit_timer.excel import (
    ExcelRecordWriter,
    LiveExcelRecordWriter,
    TEXT_NUMBER_FORMAT,
    format_timer_time,
)
from summit_timer.protocol import DataAck


def make_record(record_number: int) -> DataAck:
    return DataAck(
        device_id=1,
        record_number=record_number,
        event_number=20,
        heat_number=5,
        channel=1,
        record_type="b",
        user_string="45",
        time=datetime.datetime.strptime("01:02:03.4", "%H:%M:%S.%f").time(),
    )


def test_excel_writer_creates_headers_and_appends_records(tmp_path):
    file_path = tmp_path / "records.xlsx"
    writer = ExcelRecordWriter(file_path, "Timing")

    written = writer.append_records([make_record(1), make_record(2)])

    assert [record.record_number for record in written] == [1, 2]

    workbook = load_workbook(file_path)
    sheet = workbook["Timing"]
    assert [cell.value for cell in sheet[1]] == ExcelRecordWriter.headers
    assert sheet.cell(row=2, column=1).value == 1
    assert sheet.cell(row=2, column=2).value == 1
    assert sheet.cell(row=2, column=8).value == "01:02:03.400"
    assert sheet.cell(row=2, column=8).data_type == "s"
    assert sheet.cell(row=2, column=8).number_format == TEXT_NUMBER_FORMAT
    assert sheet.cell(row=3, column=2).value == 2
    assert not sheet.tables


def test_excel_writer_does_not_append_duplicate_records(tmp_path):
    file_path = tmp_path / "records.xlsx"
    writer = ExcelRecordWriter(file_path, "Timing")
    writer.append_records([make_record(1)])

    written = ExcelRecordWriter(file_path, "Timing").append_records(
        [make_record(1), make_record(2)]
    )

    workbook = load_workbook(file_path)
    sheet = workbook["Timing"]
    assert [record.record_number for record in written] == [2]
    assert sheet.max_row == 3
    assert not sheet.tables


def test_excel_writer_creates_output_sheet_in_existing_workbook(tmp_path):
    file_path = tmp_path / "existing.xlsx"
    workbook = Workbook()
    workbook.active.title = "Summary"
    workbook.active["A1"] = "Keep me"
    workbook.save(file_path)

    written = ExcelRecordWriter(file_path, "Timing").append_records([make_record(1)])

    workbook = load_workbook(file_path)
    assert [record.record_number for record in written] == [1]
    assert workbook["Summary"]["A1"].value == "Keep me"
    assert [cell.value for cell in workbook["Timing"][1]] == ExcelRecordWriter.headers


def test_excel_writer_appends_to_existing_output_sheet_in_workbook(tmp_path):
    file_path = tmp_path / "existing.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Timing"
    sheet.append(ExcelRecordWriter.headers)
    workbook.save(file_path)

    written = ExcelRecordWriter(file_path, "Timing").append_records([make_record(1)])

    workbook = load_workbook(file_path)
    assert [record.record_number for record in written] == [1]
    assert workbook["Timing"].max_row == 2
    assert not workbook["Timing"].tables


def test_excel_writer_rejects_existing_sheet_with_unrelated_headers(tmp_path):
    file_path = tmp_path / "existing.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Timing"
    sheet.append(["name", "score"])
    workbook.save(file_path)

    with pytest.raises(ValueError, match="does not look like a Summit output sheet"):
        ExcelRecordWriter(file_path, "Timing").append_records([make_record(1)])


def test_excel_writer_accepts_existing_sheet_with_only_blank_cells(tmp_path):
    file_path = tmp_path / "existing.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Timing"
    sheet["A10"] = None
    sheet["D4"] = None
    workbook.save(file_path)

    written = ExcelRecordWriter(file_path, "Timing").append_records([make_record(1)])

    workbook = load_workbook(file_path)
    sheet = workbook["Timing"]
    assert [record.record_number for record in written] == [1]
    assert [cell.value for cell in sheet[1]] == ExcelRecordWriter.headers
    assert sheet.cell(row=2, column=2).value == 1
    assert not sheet.tables


def test_excel_writer_uses_first_data_row_when_sheet_has_old_blank_dimensions(tmp_path):
    file_path = tmp_path / "existing.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Timing"
    sheet["H30"] = "old value"
    sheet["H30"] = None
    workbook.save(file_path)

    ExcelRecordWriter(file_path, "Timing").append_records([make_record(1)])

    workbook = load_workbook(file_path)
    sheet = workbook["Timing"]
    assert [cell.value for cell in sheet[1]] == ExcelRecordWriter.headers
    assert sheet.cell(row=2, column=2).value == 1
    assert sheet.cell(row=30, column=8).value is None
    assert not sheet.tables


def test_excel_writer_appends_under_existing_rows(tmp_path):
    file_path = tmp_path / "records.xlsx"
    writer = ExcelRecordWriter(file_path, "Timing")
    writer.append_records([make_record(1)])

    ExcelRecordWriter(file_path, "Timing").append_records([make_record(2)])

    workbook = load_workbook(file_path)
    sheet = workbook["Timing"]
    assert sheet.cell(row=3, column=2).value == 2
    assert not sheet.tables


def test_live_excel_writer_updates_cells(tmp_path):
    file_path = tmp_path / "live.xlsx"
    fake_xlwings = FakeXlwings()

    writer = LiveExcelRecordWriter(file_path, "Timing", xlwings_module=fake_xlwings)
    written = writer.append_records([make_record(1), make_record(2)])

    sheet = writer.book.sheets["Timing"]
    assert [record.record_number for record in written] == [1, 2]
    assert [
        sheet.cells[(1, column)] for column in range(1, 9)
    ] == ExcelRecordWriter.headers
    assert sheet.cells[(2, 2)] == 1
    assert sheet.cells[(2, 8)] == "01:02:03.400"
    assert sheet.formats[((2, 8), (3, 8))] == TEXT_NUMBER_FORMAT
    assert sheet.cells[(3, 2)] == 2
    assert writer.book.saved_path == str(file_path)


def test_format_timer_time_uses_three_digit_milliseconds():
    record = make_record(1)
    record.time = datetime.datetime.strptime("01:02:03.045", "%H:%M:%S.%f").time()

    assert format_timer_time(record) == "01:02:03.045"


class FakeXlwings:
    def Book(self, path=None):
        return FakeBook(path)


class FakeBook:
    def __init__(self, path=None):
        self.path = path
        self.saved_path = None
        self.sheets = FakeSheets([FakeSheet("Sheet1")])

    def save(self, path):
        self.saved_path = path


class FakeSheets:
    def __init__(self, sheets):
        self._sheets = sheets

    def __iter__(self):
        return iter(self._sheets)

    def __len__(self):
        return len(self._sheets)

    def __getitem__(self, item):
        if isinstance(item, str):
            for sheet in self._sheets:
                if sheet.name == item:
                    return sheet
            raise KeyError(item)
        return self._sheets[item]

    def add(self, name, after=None):
        sheet = FakeSheet(name)
        self._sheets.append(sheet)
        return sheet


class FakeSheet:
    def __init__(self, name):
        self.name = name
        self.cells = {}
        self.formats = {}

    @property
    def used_range(self):
        if not self.cells:
            return FakeRange(self, (1, 1), (1, 1))

        max_row = max(row for row, _ in self.cells)
        max_column = max(column for _, column in self.cells)
        return FakeRange(self, (1, 1), (max_row, max_column))

    def range(self, start, end=None):
        return FakeRange(self, start, end or start)


class FakeRange:
    def __init__(self, sheet, start, end):
        self.sheet = sheet
        self.start = start
        self.end = end
        self.row = start[0]

    @property
    def number_format(self):
        return self.sheet.formats.get((self.start, self.end))

    @number_format.setter
    def number_format(self, value):
        self.sheet.formats[(self.start, self.end)] = value

    @property
    def value(self):
        start_row, start_column = self.start
        end_row, end_column = self.end
        if self.start == self.end:
            return self.sheet.cells.get(self.start)

        values = []
        for row in range(start_row, end_row + 1):
            row_values = []
            for column in range(start_column, end_column + 1):
                row_values.append(self.sheet.cells.get((row, column)))
            values.append(row_values)

        if start_row == end_row:
            return values[0]
        return values

    @value.setter
    def value(self, values):
        start_row, start_column = self.start
        if not isinstance(values, list):
            values = [[values]]
        elif values and not isinstance(values[0], list):
            values = [values]

        for row_offset, row_values in enumerate(values):
            for column_offset, value in enumerate(row_values):
                self.sheet.cells[
                    (start_row + row_offset, start_column + column_offset)
                ] = value
