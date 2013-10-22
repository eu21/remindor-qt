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
from remindor_common.helpers import TimeDialogInfo

class TimeDialog(QDialog):
    update = Signal(str)

    def __init__(self, time_s = "", parent = None):
        super(TimeDialog, self).__init__(parent)
        helpers.setup_ui(self, "TimeDialog.ui")
        self.info = TimeDialogInfo(time_s, helpers.database_file())

        self.cancel_button = self.findChild(QPushButton, "cancel_button")
        self.ok_button = self.findChild(QPushButton, "ok_button")

        self.time_label = self.findChild(QLabel, "time_label")
        self.time_combo = self.findChild(QComboBox, "time_combo")

        self.error_label = self.findChild(QLabel, "error_label")
        self.error_label.hide()

        self.at_label = self.findChild(QLabel, "at_label")
        self.at_time = self.findChild(QTimeEdit, "at_time")

        self.every_label = self.findChild(QLabel, "every_label")
        self.every_spin = self.findChild(QSpinBox, "every_spin")
        self.mh_label = self.findChild(QLabel, "mh_label")
        self.from_label = self.findChild(QLabel, "from_label")
        self.from_time = self.findChild(QTimeEdit, "from_time")
        self.from_check = self.findChild(QCheckBox, "from_check")
        self.to_label = self.findChild(QLabel, "to_label")
        self.to_time = self.findChild(QTimeEdit, "to_time")

        self.translate()

        self.at_time.setDisplayFormat(self.info.qt_time_format)
        self.at_time.setTime(QTime.fromString(self.info.once_s, self.info.qt_time_format))
        self.from_time.setDisplayFormat(self.info.qt_time_format)
        self.from_time.setTime(QTime.fromString(self.info.from_s, self.info.qt_time_format))
        self.to_time.setDisplayFormat(self.info.qt_time_format)
        self.to_time.setTime(QTime.fromString(self.info.to_s, self.info.qt_time_format))
        self.from_check.setChecked(self.info.check)

        self.time_combo.setCurrentIndex(self.info.active)
        self.every_spin.setValue(self.info.every)

        #setup window
        self.on_time_combo_currentIndexChanged()
        self.validate_from_to()

    def translate(self):
        self.setWindowTitle(_("Edit Time"))
        self.time_label.setText(_("Time"))

        times = [
            _("Once"),
            _("Every X Minutes"),
            _("Every X Hours")
        ]

        self.time_combo.clear()
        self.time_combo.addItems(times)

        self.at_label.setText(_("At"))
        self.every_label.setText(_("Every"))
        self.from_label.setText(_("From"))
        self.to_label.setText(_("To"))
        self.error_label.setText(_("From must be before To"))

        self.cancel_button.setText(_("Cancel"))
        self.ok_button.setText(_("Ok"))

    @Slot()
    def on_from_time_timeChanged(self):
        self.validate_from_to()

    @Slot()
    def on_to_time_timeChanged(self):
        self.validate_from_to()

    def validate_from_to(self):
        if self.time_combo.currentIndex() != self.info.once and self.from_check.isChecked():
            from_s = self.from_time.time().toString(self.info.qt_time_format)
            to_s = self.to_time.time().toString(self.info.qt_time_format)

            error = self.info.validate_from_to(from_s, to_s)
            if not error:
                self.error_label.show()
            else:
                self.error_label.hide()

            return error

        return True

    @Slot()
    def on_cancel_button_pressed(self):
        self.reject()

    @Slot()
    def on_ok_button_pressed(self):
        index = self.time_combo.currentIndex()
        once_s = self.at_time.time().toString(self.info.qt_time_format)
        every = self.every_spin.value()

        from_s = ""
        to_s = ""
        if self.from_check.isChecked():
            from_s = self.from_time.time().toString(self.info.qt_time_format)
            to_s = self.to_time.time().toString(self.info.qt_time_format)

        if self.validate_from_to():
            self.update.emit(self.info.build_time(index, once_s, every, from_s, to_s))
            self.accept()

    @Slot()
    def on_time_combo_currentIndexChanged(self):
        index = self.time_combo.currentIndex()

        if index == self.info.once:
            self.at_label.show()
            self.at_time.show()
            self.every_label.hide()
            self.every_spin.hide()
            self.mh_label.hide()
            self.from_label.hide()
            self.from_time.hide()
            self.from_check.hide()
            self.to_label.hide()
            self.to_time.hide()
            self.error_label.hide()
        else:
            self.at_label.hide()
            self.at_time.hide()
            self.every_label.show()
            self.every_spin.show()
            self.mh_label.show()
            self.from_label.show()
            self.from_time.show()
            self.from_check.show()
            self.to_label.show()
            self.to_time.show()

            self.validate_from_to()

            if index == self.info.minutes:
                self.mh_label.setText(_("Minute(s)"))
            elif index == self.info.hours:
                self.mh_label.setText(_("Hour(s)"))

        self.resize(1, 1)
        self.adjustSize()
