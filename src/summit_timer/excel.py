from pathlib import Path
from typing import ClassVar

from openpyxl import Workbook, load_workbook

from summit_timer.protocol import DataAck


class ExcelRecordWriter:
    headers: ClassVar[list[str]] = [
        "device_id",
        "record_number",
        "event_number",
        "heat_number",
        "channel",
        "record_type",
        "user_string",
        "time",
    ]

    def __init__(self, file_path: str | Path, sheet_name: str):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self._written_keys: set[tuple[int, int]] = set()

    def append_records(self, records: list[DataAck]) -> list[DataAck]:
        if not records:
            return []

        workbook = self._load_workbook()
        sheet = self._get_sheet(workbook)
        self._ensure_headers(sheet)
        self._load_written_keys(sheet)

        written = []
        for record in records:
            key = (record.device_id, record.record_number)
            if key in self._written_keys:
                continue

            sheet.append(
                [
                    record.device_id,
                    record.record_number,
                    record.event_number,
                    record.heat_number,
                    record.channel,
                    record.record_type,
                    record.user_string,
                    record.time,
                ]
            )
            self._written_keys.add(key)
            written.append(record)

        if written:
            workbook.save(self.file_path)

        return written

    def _load_workbook(self):
        if self.file_path.exists():
            return load_workbook(self.file_path)
        return Workbook()

    def _get_sheet(self, workbook):
        if self.sheet_name in workbook.sheetnames:
            return workbook[self.sheet_name]

        sheet = workbook.active
        if sheet.max_row == 1 and sheet.max_column == 1 and sheet["A1"].value is None:
            sheet.title = self.sheet_name
            return sheet

        return workbook.create_sheet(self.sheet_name)

    def _ensure_headers(self, sheet):
        if sheet.max_row == 1 and sheet["A1"].value is None:
            for index, header in enumerate(self.headers, start=1):
                sheet.cell(row=1, column=index, value=header)
            return

        existing_headers = [cell.value for cell in sheet[1][: len(self.headers)]]
        if existing_headers != self.headers:
            sheet.insert_rows(1)
            for index, header in enumerate(self.headers, start=1):
                sheet.cell(row=1, column=index, value=header)

    def _load_written_keys(self, sheet):
        self._written_keys.clear()
        header_map = {cell.value: index for index, cell in enumerate(sheet[1], start=1)}
        device_column = header_map.get("device_id")
        record_column = header_map.get("record_number")
        if device_column is None or record_column is None:
            return

        for row in range(2, sheet.max_row + 1):
            device_id = sheet.cell(row=row, column=device_column).value
            record_number = sheet.cell(row=row, column=record_column).value
            if device_id is None or record_number is None:
                continue
            self._written_keys.add((int(device_id), int(record_number)))
