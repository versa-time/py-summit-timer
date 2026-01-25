from .app import App
import sys
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    q_app = QApplication([])
    app = App()
    app.show()
    sys.exit(q_app.exec())