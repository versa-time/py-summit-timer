from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QVBoxLayout,
)

from summit_timer.excel import ExcelRecordWriter, create_excel_writer


class DataWriter(QGroupBox):
    def __init__(self):
        super().__init__()
        self.file_path = ""
        self._writer = None
        self._writer_key = None
        self.setTitle("Data Writer")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open Existing")
        self.create_button = QPushButton("Create New")
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.create_button)
        layout.addLayout(button_layout)
        self.open_button.clicked.connect(self.open_existing_file)
        self.create_button.clicked.connect(self.create_new_file)
        self.live_updates_input = QCheckBox("Live Excel updates")
        self.live_updates_input.setChecked(True)
        layout.addWidget(self.live_updates_input)
        self.sheet_name_input = QLineEdit("Sheet1")
        layout.addWidget(QLabel("Sheet Name:"))
        layout.addWidget(self.sheet_name_input)

    def open_existing_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Excel File", "", "Excel Files (*.xlsx)"
        )
        self.set_file_path(file_path)

    def create_new_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Create Excel File", "", "Excel Files (*.xlsx)"
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

    def get_writer(self) -> ExcelRecordWriter | None:
        if not self.file_path:
            return None
        sheet_name = self.sheet_name_input.text().strip() or "Sheet1"
        live = self.live_updates_input.isChecked()
        writer_key = (self.file_path, sheet_name, live)
        if self._writer is None or self._writer_key != writer_key:
            self._writer = create_excel_writer(
                self.file_path,
                sheet_name,
                live=live,
            )
            self._writer_key = writer_key
        return self._writer
