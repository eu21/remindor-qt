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

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-qt')

from remindor_qt import helpers
from remindor_common.helpers import DateDialogInfo

class DateDialog(QDialog):
    update = Signal(str)

    def __init__(self, date_s = "", parent = None):
        super(DateDialog, self).__init__(parent)
        helpers.setup_ui(self, "DateDialog.ui")
        self.info = DateDialogInfo(date_s, helpers.database_file())

        self.cancel_button = self.findChild(QPushButton, "cancel_button")
        self.ok_button = self.findChild(QPushButton, "ok_button")

        self.date_label = self.findChild(QLabel, "date_label")
        self.date_combo = self.findChild(QComboBox, "date_combo")

        self.on_label = self.findChild(QLabel, "on_label")
        self.on_combo = self.findChild(QComboBox, "on_combo")
        self.on_date = self.findChild(QDateEdit, "on_date")

        self.every_label = self.findChild(QLabel, "every_label")
        self.every_combo = self.findChild(QComboBox, "every_combo")
        self.every_label2 = self.findChild(QLabel, "every_label2")
        self.every_spin = self.findChild(QSpinBox, "every_spin")
        self.days_label = self.findChild(QLabel, "days_label")
        self.from_label = self.findChild(QLabel, "from_label")
        self.from_date = self.findChild(QDateEdit, "from_date")
        self.from_check = self.findChild(QCheckBox, "from_check")
        self.to_label = self.findChild(QLabel, "to_label")
        self.to_date = self.findChild(QDateEdit, "to_date")

        self.error_label = self.findChild(QLabel, "error_label")
        self.error_label.hide()

        self.on_date.setDisplayFormat(self.info.qt_date_format)
        self.on_date.setDate(QDate.fromString(self.info.once_date, self.info.qt_date_format))
        self.from_date.setDisplayFormat(self.info.qt_date_format)
        self.from_date.setDate(QDate.fromString(self.info.from_date, self.info.qt_date_format))
        self.from_check.setChecked(self.info.check)
        self.to_date.setDisplayFormat(self.info.qt_date_format)
        self.to_date.setDate(QDate.fromString(self.info.to_date, self.info.qt_date_format))

        self.date_combo.setCurrentIndex(self.info.active)
        self.every_combo.setCurrentIndex(self.info.every_active)
        self.every_spin.setValue(self.info.every_spin)

        self.on_date_combo_currentIndexChanged()

        self.translate()

    def translate(self):
        self.date_label.setText(_("Date"))
        self.on_label.setText(_("On"))
        self.every_label.setText(_("Every"))
        self.every_label2.setText(_("Every"))
        self.from_label.setText(_("From"))
        self.to_label.setText(_("To"))
        self.error_label.setText(_("From must be before To"))

        date_types = [
            _("Once"),
            _("Every Day"),
            _("Every X Days"),
            _("Every Xth of the Month"),
            _("Every <day>"),
            _("Every Other Day"),
            _("Next X Days")
        ]

        self.date_combo.clear()
        self.date_combo.addItems(date_types)

        dates = [
            _("Other"),
            _("Today"),
            _("Tomorrow"),
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
            _("Sunday"),
            _("Christmas")
        ]

        self.on_combo.clear()
        self.on_combo.addItems(dates)

        weekdays = [
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
            _("Sunday"),
            _("Weekday"),
            _("Weekend")
        ]

        self.every_combo.clear()
        self.every_combo.addItems(weekdays)

        self.cancel_button.setText(_("Cancel"))
        self.ok_button.setText(_("Ok"))

    @Slot()
    def on_from_date_dateChanged(self):
        self.validate_from_to()

    @Slot()
    def on_to_date_dateChanged(self):
        self.validate_from_to()

    @Slot()
    def on_cancel_button_pressed(self):
        self.reject()

    @Slot()
    def on_ok_button_pressed(self):
        index = self.date_combo.currentIndex()
        once_index = self.on_combo.currentIndex()
        once_date = self.on_date.date().toString(self.info.qt_date_format)
        every_index = self.every_combo.currentIndex()
        every_spin = self.every_spin.value()

        from_date = ""
        to_date = ""
        if self.from_check.isChecked():
            from_date = self.from_date.date().toString(self.info.qt_date_format)
            to_date = self.to_date.date().toString(self.info.qt_date_format)

        if self.validate_from_to():
            self.update.emit(self.info.build_date(index, once_index, once_date, every_index, every_spin, from_date, to_date))
            self.accept()

    @Slot()
    def on_on_combo_currentIndexChanged(self):
        index = self.on_combo.currentIndex()

        if index == 0:
            self.on_date.show()
        else:
            self.on_date.hide()

    @Slot()
    def on_date_combo_currentIndexChanged(self):
        index = self.date_combo.currentIndex()

        self.on_label.hide()
        self.on_combo.hide()
        self.on_date.hide()
        self.every_label.hide()
        self.every_combo.hide()
        self.every_label2.hide()
        self.every_spin.hide()
        self.days_label.hide()
        self.from_label.hide()
        self.from_date.hide()
        self.from_check.hide()
        self.to_label.hide()
        self.to_date.hide()
        self.error_label.hide()

        if index == self.info.once:
            self.on_label.show()
            self.on_combo.show()
            self.on_on_combo_currentIndexChanged()
        elif index == self.info.every_days:
            self.every_label2.show()
            self.every_label2.setText(_("Every"))
            self.every_spin.show()
            self.every_spin.setMaximum(600)
            self.days_label.show()
            self.days_label.setText(_("Day(s)"))
        elif index == self.info.every_month:
            self.every_label2.show()
            self.every_label2.setText(_("Every"))
            self.every_spin.show()
            self.every_spin.setMaximum(12)
            self.days_label.show()
            self.days_label.setText(_("of the month"))
        elif index == self.info.every:
            self.every_label.show()
            self.every_combo.show()
        elif index == self.info.next_days:
            self.every_label2.show()
            self.every_label2.setText(_("Next"))
            self.every_spin.show()
            self.every_spin.setMaximum(600)
            self.days_label.show()
            self.days_label.setText(tr.days)

        if not (index == self.info.once):
            self.from_label.show()
            self.from_date.show()
            self.from_check.show()

            if not (index == self.info.next_days):
                self.to_label.show()
                self.to_date.show()

            self.validate_from_to()

        self.resize(1, 1)
        self.adjustSize()

    def validate_from_to(self):
        if self.date_combo.currentIndex() != self.info.once and self.date_combo.currentIndex() != self.info.next_days and self.from_check.isChecked():
            from_s = self.from_date.date().toString(self.info.qt_date_format)
            to_s = self.to_date.date().toString(self.info.qt_date_format)

            error = self.info.validate_from_to(from_s, to_s)
            if not error:
                self.error_label.show()
            else:
                self.error_label.hide()

            return error

        return True