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
gettext.textdomain('remindor-qt')

import logging
logger = logging.getLogger('remindor_qt')

from remindor_qt import helpers
from remindor_common.helpers import insert_values

class CommandDialog(QDialog):
    update = Signal(str)

    def __init__(self, command = "", parent = None):
        super(CommandDialog, self).__init__(parent)
        helpers.setup_ui(self, "CommandDialog.ui")

        self.insert_combo = self.findChild(QComboBox, "insert_combo")
        self.command_edit = self.findChild(QLineEdit, "command_edit")
        self.command_edit.setText(command)

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