from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from summit_timer.excel import ExcelRecordWriter, create_excel_writer

DEFAULT_SHEET_NAME = "Sheet1"
SETTINGS_ORGANIZATION = "SummitTimer"
SETTINGS_APPLICATION = "SummitLink"
SHEET_NAME_SETTING = "excel/sheet_name"
FILE_PATH_SETTING = "excel/file_path"


class DataWriter(QGroupBox):
    def __init__(self, settings: QSettings | None = None):
        super().__init__()
        self.settings = settings or QSettings(
            SETTINGS_ORGANIZATION, SETTINGS_APPLICATION
        )
        self.file_path = ""
        self._writer = None
        self._writer_key = None
        self.setTitle("Data Writer")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)
        self.open_button = QPushButton("Open Existing")
        layout.addWidget(self.open_button)
        self.open_button.clicked.connect(self.open_existing_file)
        self.sheet_name_input = QLineEdit(self.load_sheet_name())
        self.sheet_name_input.editingFinished.connect(self.save_sheet_name)
        layout.addWidget(QLabel("Sheet Name:"))
        layout.addWidget(self.sheet_name_input)
        self.restore_file_path()

    def open_existing_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Excel File", "", "Excel Files (*.xlsx)"
        )
        self.set_file_path(file_path)

    def set_file_path(self, file_path: str):
        if file_path:
            if not file_path.endswith(".xlsx"):
                file_path = f"{file_path}.xlsx"
            self.file_path = file_path
            self._writer = None
            self._writer_key = None
            self.file_label.setText(file_path)
            self.save_file_path()

    def get_writer(self) -> ExcelRecordWriter | None:
        if not self.file_path:
            return None
        sheet_name = self.current_sheet_name()
        writer_key = (self.file_path, sheet_name)
        if self._writer is None or self._writer_key != writer_key:
            self._writer = create_excel_writer(
                self.file_path,
                sheet_name,
            )
            self._writer_key = writer_key
        return self._writer

    def current_sheet_name(self) -> str:
        return self.sheet_name_input.text().strip() or DEFAULT_SHEET_NAME

    def load_sheet_name(self) -> str:
        sheet_name = self.settings.value(SHEET_NAME_SETTING, DEFAULT_SHEET_NAME)
        if not isinstance(sheet_name, str) or not sheet_name.strip():
            return DEFAULT_SHEET_NAME
        return sheet_name

    def save_sheet_name(self):
        self.settings.setValue(SHEET_NAME_SETTING, self.current_sheet_name())

    def restore_file_path(self):
        file_path = self.settings.value(FILE_PATH_SETTING, "")
        if not isinstance(file_path, str) or not file_path:
            return

        if not Path(file_path).exists():
            self.settings.setValue(FILE_PATH_SETTING, "")
            return

        self.file_path = file_path
        self.file_label.setText(file_path)

    def save_file_path(self):
        self.settings.setValue(FILE_PATH_SETTING, self.file_path)
