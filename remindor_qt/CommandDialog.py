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

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-common')

import logging
logger = logging.getLogger('remindor_qt')

from remindor_qt import helpers
from remindor_common.helpers import insert_values

class CommandDialog(QDialog):
    update = Signal(str)

    def __init__(self, command = "", parent = None):
        super(CommandDialog, self).__init__(parent)
        helpers.setup_ui(self, "CommandDialog.ui")

        self.insert_button = self.findChild(QPushButton, "insert_button")
        self.insert_combo = self.findChild(QComboBox, "insert_combo")

        self.command_label = self.findChild(QLabel, "command_label")
        self.command_edit = self.findChild(QLineEdit, "command_edit")
        self.command_edit.setText(command)

        self.cancel_button = self.findChild(QPushButton, "cancel_button")
        self.ok_button = self.findChild(QPushButton, "ok_button")

        self.translate()

    def translate(self):
        self.setWindowTitle(_("Edit Command"))
        self.insert_button.setText(_("Insert"))

        inserts = [
            _("Date"),
            _("Month"),
            _("Month Name"),
            _("Day"),
            _("Day Name"),
            _("Day of Year"),
            _("Year"),
            _("Time"),
            _("Hour (24)"),
            _("Hour (12)"),
            _("Minutes"),
            _("Seconds"),
            _("Microseconds"),
            _("Sound File/Path"),
            _("Sound File")
        ]

        self.insert_combo.clear()
        self.insert_combo.addItems(inserts)

        self.command_label.setText(_("Command"))
        self.cancel_button.setText(_("Cancel"))
        self.ok_button.setText(_("Ok"))

    @Slot()
    def on_ok_button_pressed(self):
        self.update.emit(self.command_edit.text())
        self.accept()

    @Slot()
    def on_cancel_button_pressed(self):
        self.reject()

    @Slot()
    def on_insert_button_pressed(self):
        index = self.insert_combo.currentIndex()
        self.command_edit.insert(insert_values[index])

    @Slot()
    def on_command_button_pressed(self):
        caption = _("Choose Command")
        command_dir = "/usr/bin"
        file_filter = _("All Files (*)")

        (filename, selected_filter) = QFileDialog.getOpenFileName(self, caption, command_dir, file_filter)
        self.command_edit.setText(filename)
