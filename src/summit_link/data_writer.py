from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from summit_timer.excel import ExcelRecordWriter


class DataWriter(QGroupBox):
    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.setTitle("Data Writer")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)
        self.select_button = QPushButton("Choose Excel File")
        layout.addWidget(self.select_button)
        self.select_button.clicked.connect(self.select_file)
        self.sheet_name_input = QLineEdit("Sheet1")
        layout.addWidget(QLabel("Sheet Name:"))
        layout.addWidget(self.sheet_name_input)

    def select_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Choose Excel File", "", "Excel Files (*.xlsx)"
        )
        if file_path:
            if not file_path.endswith(".xlsx"):
                file_path = f"{file_path}.xlsx"
            self.file_path = file_path
            self.file_label.setText(file_path)

    def get_writer(self) -> ExcelRecordWriter | None:
        if not self.file_path:
            return None
        sheet_name = self.sheet_name_input.text().strip() or "Sheet1"
        return ExcelRecordWriter(self.file_path, sheet_name)
