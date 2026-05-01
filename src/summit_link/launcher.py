import sys

from PySide6.QtWidgets import QApplication

from summit_link.app import App


def main() -> int:
    q_app = QApplication(sys.argv)
    app = App()
    app.show()
    return q_app.exec()


if __name__ == "__main__":
    sys.exit(main())
