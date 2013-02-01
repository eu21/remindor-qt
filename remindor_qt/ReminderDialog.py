# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2012 Brian Douglass bhdouglass@gmail.com
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

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-qt')

import logging
logger = logging.getLogger('remindor_qt')

from remindor_qt import helpers
from remindor_qt.remindor_qtconfig import get_data_file

from remindor_common.helpers import ReminderDialogInfo

class ReminderDialog(QDialog):
    added = Signal(int)

    def __init__(self, parent = None):
        super(ReminderDialog, self).__init__(parent)
        helpers.setup_ui(self, "ReminderDialog.ui")

        self.label_edit = self.findChild(QLineEdit, "label_edit")
        self.time_edit = self.findChild(QLineEdit, "time_edit")
        self.date_edit = self.findChild(QLineEdit, "date_edit")
        self.command_edit = self.findChild(QLineEdit, "command_edit")
        self.notes_edit = self.findChild(QPlainTextEdit, "notes_edit")

        self.popup_check = self.findChild(QCheckBox, "popup_check")
        self.dialog_check = self.findChild(QCheckBox, "dialog_check")
        self.boxcar_check = self.findChild(QCheckBox, "boxcar_check")

        self.sound_check = self.findChild(QCheckBox, "sound_check")
        self.file_edit = self.findChild(QLineEdit, "file_edit")
        self.length_spin = self.findChild(QSpinBox, "length_spin")
        self.loop_check = self.findChild(QCheckBox, "loop_check")

        self.insert_combo = self.findChild(QComboBox, "insert_combo");

        self.info = ReminderDialogInfo(helpers.database_file())
        self.set_data(self.info.label, self.info.time, self.info.date, self.info.command,
                      self.info.notes, self.info.popup, self.info.dialog, self.info.boxcar,
                      self.info.sound_file, self.info.sound_length, self.info.sound_loop)

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
                                          boxcar, play, sound_file, sound_length, sound_loop)

        if status == self.info.ok:
            self.added.emit(id)
            self.accept()
        else:
            print status #TODO: popup error

    @Slot()
    def on_cancel_button_pressed(self):
        self.reject()

    @Slot()
    def on_help_button_pressed(self):
        helpers.show_uri(self, "ghelp:%s" % helpers.get_help_uri('add'))

    @Slot()
    def on_time_button_pressed(self):
        pass

    @Slot()
    def on_date_button_pressed(self):
        pass

    @Slot()
    def on_command_button_pressed(self):
        pass

    @Slot()
    def on_notes_button_pressed(self):
        index = self.insert_combo.currentIndex()
        self.notes_edit.insertPlainText(self.info.insert_values[index])

    @Slot()
    def on_file_button_pressed(self):
        caption = _("Choose Sound")
        sound_dir = get_data_file('media', 'sounds')
        file_filter = _("Sounds (*.mp3 *.ogg *.wav);;MP3 (*.mp3);;Ogg (*.ogg);;WAVE (*.wav)");

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

    def set_data(self, label, time, date, command, notes, popup,
                 dialog, boxcar, sound_file, length, loop):
        self.label_edit.setText(label);
        self.time_edit.setText(time);
        self.date_edit.setText(date);
        self.command_edit.setText(command);
        self.notes_edit.setPlainText(notes);

        self.popup_check.setChecked(popup);
        self.dialog_check.setChecked(dialog);
        self.boxcar_check.setChecked(boxcar);

        if sound_file is not None and not sound_file == "":
            self.sound_check.setChecked(True);
        else:
            self.sound_check.setChecked(False);

        self.file_edit.setText(sound_file);
        self.length_spin.setValue(length);
        self.loop_check.setChecked(loop);