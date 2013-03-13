# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Brian Douglass bhdouglass@gmail.com
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

import logging
logger = logging.getLogger('remindor_qt')

from remindor_qt import helpers
from remindor_qt.CommandDialog import CommandDialog
from remindor_qt.DateDialog import DateDialog
from remindor_qt.TimeDialog import TimeDialog
from remindor_qt.remindor_qtconfig import get_data_file

from remindor_common.helpers import ReminderDialogInfo, insert_values, valid_date, valid_time
from remindor_common import datetimeutil, database as db
from remindor_common import translations as tr

class ReminderDialog(QDialog):
    added = Signal(int)
    delete_id = -1

    def __init__(self, parent = None):
        super(ReminderDialog, self).__init__(parent)
        helpers.setup_ui(self, "ReminderDialog.ui")

        self.help_button = self.findChild(QPushButton, "help_button")
        self.cancel_button = self.findChild(QPushButton, "cancel_button")
        self.add_button = self.findChild(QPushButton, "add_button")
        self.save_button = self.findChild(QPushButton, "save_button")
        self.save_button.hide()

        self.tabs = self.findChild(QTabWidget, "tabs")

        self.label_label = self.findChild(QLabel, "label_label")
        self.time_label = self.findChild(QLabel, "time_label")
        self.date_label = self.findChild(QLabel, "date_label")
        self.command_label = self.findChild(QLabel, "command_label")
        self.notes_label = self.findChild(QLabel, "notes_label")

        self.label_edit = self.findChild(QLineEdit, "label_edit")
        self.time_edit = self.findChild(QLineEdit, "time_edit")
        self.date_edit = self.findChild(QLineEdit, "date_edit")
        self.command_edit = self.findChild(QLineEdit, "command_edit")
        self.notes_edit = self.findChild(QPlainTextEdit, "notes_edit")

        self.time_button = self.findChild(QPushButton, "time_button")
        self.date_button = self.findChild(QPushButton, "date_button")
        self.command_button = self.findChild(QPushButton, "command_button")
        self.notes_button = self.findChild(QPushButton, "notes_button")

        self.time_error = self.findChild(QToolButton, "time_error")
        self.time_error.hide()
        self.date_error = self.findChild(QToolButton, "date_error")
        self.date_error.hide()

        self.popup_check = self.findChild(QCheckBox, "popup_check")
        self.dialog_check = self.findChild(QCheckBox, "dialog_check")
        self.boxcar_check = self.findChild(QCheckBox, "boxcar_check")
        self.boxcar_label = self.findChild(QLabel, "boxcar_label")
        self.boxcar_label.hide()

        self.sound_label = self.findChild(QLabel, "sound_label")
        self.file_label = self.findChild(QLabel, "file_label")
        self.length_label = self.findChild(QLabel, "length_label")
        self.loop_label = self.findChild(QLabel, "loop_label")
        self.length_label2 = self.findChild(QLabel, "length_label2")

        self.sound_check = self.findChild(QCheckBox, "sound_check")
        self.file_edit = self.findChild(QLineEdit, "file_edit")
        self.length_spin = self.findChild(QSpinBox, "length_spin")
        self.loop_check = self.findChild(QCheckBox, "loop_check")

        self.insert_combo = self.findChild(QComboBox, "insert_combo");

        self.info = ReminderDialogInfo(helpers.database_file())
        self.set_data(self.info.label, self.info.time, self.info.date, self.info.command,
                      self.info.notes, self.info.popup, self.info.dialog, self.info.boxcar,
                      self.info.sound_file, self.info.sound_length, self.info.sound_loop)

    def translate(self):
        self.setWindowTitle(tr.add_reminder)

        self.help_button.setText(tr.help)
        self.cancel_button.setText(tr.cancel)
        self.add_button.setText(tr.add)
        self.save_button.setText(tr.save)

        self.insert_combo.clear()
        self.insert_combo.addItems(tr.inserts)

        self.tabs.setTabText(0, tr.reminder)
        self.label_label.setText(tr.label)
        self.time_label.setText(tr.time)
        self.date_label.setText(tr.date)
        self.command_label.setText(tr.command)
        self.notes_label.setText(tr.notes)

        self.time_button.setText(tr.edit)
        self.date_button.setText(tr.edit)
        self.command_button.setText(tr.edit)
        self.help_button.setText(tr.insert)

        self.tabs.setTabText(0, tr.notification)
        self.popup_check.setText(tr.popup)
        self.dialog_check.setText(tr.dialog)
        #self.boxcar_check #doesn't need translated

        self.tabs.setTabText(0, tr.sound)
        self.sound_label.setText(tr.play_sound)
        self.file_label.setText(tr.sound_file)
        self.length_label.setText(tr.play_length)
        self.loop_label.setText(tr.loop)
        self.length_label2.setText(tr.play_length2)

    @Slot()
    def on_add_button_pressed(self):
        label = self.label_edit.text()
        time = self.time_edit.text()
        date = self.date_edit.text()
        command = self.command_edit.text()
        notes = self.notes_edit.document().toPlainText()
        popup = self.popup_check.isChecked()
        dialog = self.dialog_check.isChecked()
        boxcar = self.boxcar_check.isChecked()
        play = self.sound_check.isChecked()
        sound_file = self.file_edit.text()
        sound_length = self.length_spin.value()
        sound_loop = self.loop_check.isChecked()

        (status, id) = self.info.reminder(label, time, date, command, notes, popup, dialog,
                                          boxcar, play, sound_file, sound_length, sound_loop,
                                          self.delete_id, True)

        if status == self.info.ok:
            self.added.emit(id)
            self.accept()
        else:
            if status == self.info.file_error:
                title = tr.file_not_exist_title
                message = ""
                if sound_file != "":
                    message = "%s\n\n%s" % (tr.file_not_exist_message, sound_file)
                else:
                    message = tr.file_not_exist_choose
                QMessageBox.warning(self, title, message)
            elif status == self.info.time_error:
                self.time_error.show()
                self.time_edit.setFocus()
            elif status == self.info.date_error:
                self.date_error.show()
                self.date_edit.setFocus()
            elif status == self.info.notify_warn:
                title = tr.empty_notify_title
                message = tr.empty_notify_message
                ans = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if ans == QMessageBox.Yes:
                    (status, id) = self.info.reminder(label, time, date, command, notes,
                                                      popup, dialog, boxcar, play,
                                                      sound_file, sound_length, sound_loop,
                                                      self.delete_id)
                    #already checked the status (boxcar is the last check)
                    self.added.emit(id)
                    self.accept()

    @Slot()
    def on_cancel_button_pressed(self):
        self.reject()

    @Slot()
    def on_help_button_pressed(self):
        helpers.show_html_help("add")

    @Slot()
    def on_time_button_pressed(self):
        simple_time = datetimeutil.str_time_simplify(self.time_edit.text())
        fixed_time = datetimeutil.fix_time_format(simple_time, self.info.time_format)

        dialog = TimeDialog(fixed_time, self)
        dialog.update.connect(self.time_updated)
        dialog.exec_()

    @Slot()
    def time_updated(self, time_s):
        self.time_edit.setText(time_s)

    @Slot()
    def on_time_edit_textEdited(self):
        if valid_time(self.time_edit.text()):
            self.time_error.hide()
        else:
            self.time_error.show()

    @Slot()
    def on_date_button_pressed(self):
        simple_date = datetimeutil.str_date_simplify(self.date_edit.text(), self.info.date_format)
        fixed_date = datetimeutil.fix_date_format(simple_date, self.info.date_format)

        dialog = DateDialog(fixed_date, self)
        dialog.update.connect(self.date_updated)
        dialog.exec_()

    @Slot()
    def date_updated(self, date_s):
        self.date_edit.setText(date_s)

    @Slot()
    def on_date_edit_textEdited(self):
        if valid_date(self.date_edit.text(), self.info.date_format):
            self.date_error.hide()
        else:
            self.date_error.show()

    @Slot()
    def on_command_button_pressed(self):
        dialog = CommandDialog(self.command_edit.text(), self)
        dialog.update.connect(self.command_updated)
        dialog.exec_()

    @Slot()
    def command_updated(self, command):
        self.command_edit.setText(command)

    @Slot()
    def on_notes_button_pressed(self):
        index = self.insert_combo.currentIndex()
        self.notes_edit.insertPlainText(insert_values[index])

    @Slot()
    def on_file_button_pressed(self):
        caption = tr.choose_sound_title
        sound_dir = get_data_file('media', 'sounds')
        file_filter = tr.choose_sound_filter

        (filename, selected_filter) = QFileDialog.getOpenFileName(self, caption, sound_dir, file_filter)
        self.file_edit.setText(filename)

    @Slot()
    def on_sound_check_toggled(self):
        if not self.sound_check.isChecked():
            self.length_spin.setEnabled(False)
        else:
            if self.loop_check.isChecked():
                self.length_spin.setEnabled(False)
            else:
                self.length_spin.setEnabled(True)

    def edit(self, reminder):
        self.save_button.show()
        self.add_button.hide()
        self.setWindowTitle(tr.edit_reminder)

        self.database = db.Database(helpers.database_file())
        r = self.database.alarm(reminder)
        self.database.close()

        self.set_data(r.label, datetimeutil.fix_time_format(r.time, self.info.time_format),
            datetimeutil.fix_date_format(r.date, self.info.date_format), r.command, r.notes,
            r.notification, r.dialog, r.boxcar, r.sound_file, r.sound_length, r.sound_loop)

        self.delete_id = reminder

    def set_data(self, label, time, date, command, notes, popup,
                 dialog, boxcar, sound_file, length, loop):
        self.label_edit.setText(label)
        self.time_edit.setText(time)
        self.date_edit.setText(date)
        self.command_edit.setText(command)
        self.notes_edit.setPlainText(notes)

        self.popup_check.setChecked(popup)
        self.dialog_check.setChecked(dialog)
        self.boxcar_check.setChecked(boxcar)

        if not self.info.boxcar_ok:
            self.boxcar_check.setChecked(False)
            self.boxcar_check.setDisabled(True)
            self.boxcar_label.show()

        if sound_file is not None and not sound_file == "":
            self.sound_check.setChecked(True)
        else:
            self.sound_check.setChecked(True) #to trigger disabling of elements
            self.sound_check.setChecked(False)

        self.file_edit.setText(sound_file)
        self.length_spin.setValue(length)
        self.loop_check.setChecked(loop)
        self.loop_check.setText(tr.loop_times % self.info.sound_loop_times)