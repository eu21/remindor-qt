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

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-common')

import logging
logger = logging.getLogger('remindor_qt')

from remindor_qt import helpers

from remindor_common.helpers import SimpleDialogInfo

class SimpleDialog(QDialog):
    added = Signal(int)

    def __init__(self, parent = None):
        super(SimpleDialog, self).__init__(parent)
        helpers.setup_ui(self, "SimpleDialog.ui")

        self.info = SimpleDialogInfo(helpers.database_file())

        self.reminder_edit = self.findChild(QLineEdit, "reminder_edit")
        self.reminder_label = self.findChild(QLabel, "reminder_label")
        self.reminder_error = self.findChild(QToolButton, "reminder_error")
        self.reminder_error.hide()

        self.help_button = self.findChild(QPushButton, "help_button")
        self.cancel_button = self.findChild(QPushButton, "cancel_button")
        self.add_button = self.findChild(QPushButton, "add_button")

        self.translate()

        self.info = SimpleDialogInfo(helpers.database_file())
        self.show_label_error = False

    def translate(self):
        self.setWindowTitle(_("Add Simple Reminder"))
        self.reminder_label.setText(_("Remind me to..."))

        self.help_button.setText(_("Help"))
        self.cancel_button.setText(_("Cancel"))
        self.add_button.setText(_("Add"))

    @Slot()
    def on_reminder_edit_textEdited(self):
        text = self.reminder_edit.text()
        (valid, date_s, time_s, label) = self.info.validate(text)

        if label == text and not self.show_label_error:
            valid = True

        if label != text and not self.show_label_error:
            self.show_label_error = True

        if valid:
            self.reminder_error.hide()
        else:
            self.reminder_error.show()

    @Slot()
    def on_help_button_pressed(self):
        helpers.show_html_help("simple-add")

    @Slot()
    def on_cancel_button_pressed(self):
        self.reject()

    @Slot()
    def on_add_button_pressed(self):
        id = self.info.reminder(self.reminder_edit.text())
        if id != None:
            self.added.emit(id)
            self.accept()
        else:
            self.reminder_error.show()
            self.show_label_error = True
