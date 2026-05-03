import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from summit_link.data_writer import DataWriter, FILE_PATH_SETTING, SHEET_NAME_SETTING


class FakeSettings:
    def __init__(self, values=None):
        self.values = values or {}

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value


def ensure_app():
    return QApplication.instance() or QApplication([])


def test_data_writer_restores_saved_sheet_name():
    ensure_app()
    writer = DataWriter(settings=FakeSettings({SHEET_NAME_SETTING: "Timing"}))

    assert writer.current_sheet_name() == "Timing"


def test_data_writer_saves_sheet_name():
    ensure_app()
    settings = FakeSettings()
    writer = DataWriter(settings=settings)

    writer.sheet_name_input.setText("RaceDay")
    writer.save_sheet_name()

    assert settings.values[SHEET_NAME_SETTING] == "RaceDay"


def test_data_writer_restores_saved_existing_file_path(tmp_path):
    ensure_app()
    file_path = tmp_path / "timing.xlsx"
    file_path.touch()

    writer = DataWriter(settings=FakeSettings({FILE_PATH_SETTING: str(file_path)}))

    assert writer.file_path == str(file_path)
    assert writer.file_label.text() == str(file_path)


def test_data_writer_ignores_saved_missing_file_path(tmp_path):
    ensure_app()
    missing_path = tmp_path / "missing.xlsx"
    settings = FakeSettings({FILE_PATH_SETTING: str(missing_path)})

    writer = DataWriter(settings=settings)

    assert writer.file_path == ""
    assert writer.file_label.text() == "No file selected"
    assert settings.values[FILE_PATH_SETTING] == ""


def test_data_writer_saves_selected_file_path(tmp_path):
    ensure_app()
    settings = FakeSettings()
    file_path = tmp_path / "selected.xlsx"

    writer = DataWriter(settings=settings)
    writer.set_file_path(str(file_path))

    assert settings.values[FILE_PATH_SETTING] == str(file_path)
