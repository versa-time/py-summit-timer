from PySide6.QtWidgets import QWidget, QGroupBox, QFileDialog, QVBoxLayout, QPushButton, QLabel, QLineEdit

class DataWriter(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Data Writer")
        # File selector, then sheet name
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)
        self.select_button = QPushButton("Select Excel File")
        layout.addWidget(self.select_button)
        self.select_button.clicked.connect(self.select_file)
        self.sheet_name_input = QLineEdit("Sheet1")
        layout.addWidget(QLabel("Sheet Name:"))
        layout.addWidget(self.sheet_name_input)
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            self.file_label.setText(file_path)