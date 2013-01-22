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

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-qt')

import logging
logger = logging.getLogger('remindor_qt')

from remindor_qt import helpers

from remindor_common.helpers import QuickDialogInfo

class QuickDialog(QDialog):
    added = Signal(int)

    def __init__(self, parent = None):
        super(QuickDialog, self).__init__(parent)
        helpers.setup_ui(self, "QuickDialog.ui")

        self.info = QuickDialogInfo(helpers.database_file())

        self.label_edit = self.findChild(QLineEdit, "label_edit")
        self.label_edit.setText(self.info.label)

        self.value_label = self.findChild(QLabel, "value_label")
        self.value_label.setNum(self.info.minutes)

        self.in_slider = self.findChild(QSlider, "in_slider")
        self.in_slider.setValue(self.info.minutes)

        self.in_spin = self.findChild(QSpinBox, "in_spin")
        self.in_spin.setValue(self.info.minutes)

        self.info_label = self.findChild(QLabel, "info_label")
        self.info_label.setText(self.info.info)
        if not self.info.show_info:
            self.info_label.hide()

        if self.info.show_slider:
            self.in_spin.hide()
            self.findChild(QLabel, "in_label2").hide()
            self.findChild(QLabel, "minutes_label2").hide()
        else:
            self.in_slider.hide()
            self.value_label.hide()
            self.findChild(QLabel, "in_label").hide()
            self.findChild(QLabel, "minutes_label2").hide()

    @Slot()
    def on_cancel_button_pressed(self):
        self.reject()

    @Slot()
    def on_add_button_pressed(self):
        #in_slider and in_spin are connected, so they always have the same value
        id = self.info.reminder(self.label_edit.text(), self.in_slider.value())
        self.added.emit(id)
        self.accept()