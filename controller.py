from PyQt6.QtWidgets import QApplication, QMessageBox, QTableWidgetItem
import PyQt6.QtCore as QtCore
import sys
import traceback
import threading

from mainwindow import MainWindow
from weekly_schedule_edit import WeeklyScheduleEditDialog
from model import SchoolBellModel
from utils import getWeekdayNameByIndex
from play_sounds.play_sounds_controller import PlaySoundsController
from play_sounds.play_sounds_thread import main_sounds_thread
from constants import REC_TYPE_SINGLE_FILE, REC_TYPE_MUSIC_FOLDER

class SchoolBellController:
    def __init__(self, application_argv):
        try:
            self.app = QApplication(sys.argv)
            self.main_window = MainWindow(self)
            self.model = SchoolBellModel()
            self.play_sounds_controller = PlaySoundsController(self.model)
        except Exception as e:
            self.handle_error(e)

    def run_application(self):
        try:
            self.main_window.show()
            self.refresh_grid()
            self.start_play_sounds_thread()
            sys.exit(self.app.exec())
        except Exception as e:
            self.handle_error(e)

    def handle_error(self, exception):
        try:
            print(exception.__traceback__)
            print(traceback.format_exc())
            QMessageBox.critical(self.main_window, "Error", "Error: '" + str(exception) + "'")
        except Exception as e:
            print(e)

    def handle_new_record_button(self):

        def add_new_record_single_file():
            new_record = { 'description' : dlg.ui.descriptionLineEdit.text(), \
                           'start_weekday_index' : dlg.ui.startWeekdayComboBox.currentIndex(), \
                           'end_weekday_index' : dlg.ui.endWeekdayComboBox.currentIndex(), \
                           'start_time' : dlg.ui.timeEdit.time(), \
                           'end_time' : None, \
                           'rec_type' : REC_TYPE_SINGLE_FILE, \
                           'file_name' : dlg.ui.fileNameLineEdit.text() \
                          }

            self.model.add_new_record(new_record)

        def add_new_record_music_folder():
            new_record = { 'description' : dlg.ui.descriptionLineEdit.text(), \
                           'start_weekday_index' : dlg.ui.startWeekdayComboBox.currentIndex(), \
                           'end_weekday_index' : dlg.ui.endWeekdayComboBox.currentIndex(), \
                           'start_time' : dlg.ui.startTimeEdit.time(),
                           'end_time' : dlg.ui.endTimeEdit.time(),
                           'rec_type' : REC_TYPE_MUSIC_FOLDER,
                           'folder_name' : dlg.ui.folderNameLineEdit.text() \
                          }

            self.model.add_new_record(new_record)

        try:
            dlg = WeeklyScheduleEditDialog(self)
            button = dlg.exec()

            if not self.isOkKeyPressedInDialog(button):
                return

            if dlg.ui.singleFileRadioButton.isChecked():
                add_new_record_single_file()
            else:
                add_new_record_music_folder()

            self.refresh_grid()

        except Exception as e:
            self.handle_error(e)

    def isOkKeyPressedInDialog(self, dialogResult):
        if dialogResult == 1:
            return True
        else:
            return False

    def refresh_grid(self):

        self.main_window.ui.scheduleTable.setRowCount(0)

        row = 0
        for record in self.model.records:
            self.main_window.ui.scheduleTable.insertRow(row)

            checkBox = QTableWidgetItem(record['active'])
            checkBox.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable |
                              QtCore.Qt.ItemFlag.ItemIsEnabled )
            if record['active']:
                checkBox.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                checkBox.setCheckState(QtCore.Qt.CheckState.Unchecked)

            self.main_window.ui.scheduleTable.setItem(row, 0, checkBox)
            self.main_window.ui.scheduleTable.setItem(row, 1, QTableWidgetItem(self.output_weekdays(record)))
            self.main_window.ui.scheduleTable.setItem(row, 2, QTableWidgetItem(self.output_time(record)))
            self.main_window.ui.scheduleTable.setItem(row, 3, QTableWidgetItem(record["description"]))
            self.main_window.ui.scheduleTable.setItem(row, 4, QTableWidgetItem(self.output_file_folder(record)))
            row = row + 1

    def output_weekdays(self, record):
        return getWeekdayNameByIndex(record["start_weekday_index"]) + ' - ' + \
               getWeekdayNameByIndex(record["end_weekday_index"])

    def output_time(self, record):
        if record['rec_type'] == REC_TYPE_SINGLE_FILE:
            return record["start_time"].toString()
        else:
            return record["start_time"].toString() + ' - ' + record["end_time"].toString()
    def output_file_folder(self, record):
        if record['rec_type'] == REC_TYPE_SINGLE_FILE:
            return '1 file: ' + record['file_name']
        else:
            return 'all files in: ' + record['folder_name']

    def perform_play_sounds_actions(self):
        self.play_sounds_controller.perform_play_sounds_actions()

    def play_sound_file_for_preview(self, file_name_with_full_path):
        self.play_sounds_controller.play_sound_file_by_path(file_name_with_full_path)

    def start_play_sounds_thread(self):
        thread = threading.Timer(1, main_sounds_thread, [self])
        thread.setDaemon(True)
        thread.start()

    def test_play_music(self):
        self.play_sounds_controller.test_play_music()