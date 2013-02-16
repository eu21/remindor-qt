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

import logging
logger = logging.getLogger('remindor_qt')

from remindor_qt import helpers
from remindor_qt.CommandDialog import CommandDialog
from remindor_qt.DateDialog import DateDialog
from remindor_qt.TimeDialog import TimeDialog

from remindor_common.helpers import rgb_to_hex, PreferencesDialogInfo
from remindor_common import datetimeutil

class PreferencesDialog(QDialog):
    update = Signal()

    def __init__(self, parent = None):
        super(PreferencesDialog, self).__init__(parent)
        helpers.setup_ui(self, "PreferencesDialog.ui")
        self.info = PreferencesDialogInfo(helpers.database_file())
        self.settings = self.info.settings
        self.boxcar_info = self.info.services.service("boxcar")

        self.label_edit = self.findChild(QLineEdit, "label_edit")
        self.label_edit.setText(self.settings.label)
        self.time_edit = self.findChild(QLineEdit, "time_edit")
        self.time_edit.setText(self.settings.time)
        self.date_edit = self.findChild(QLineEdit, "date_edit")
        self.date_edit.setText(self.settings.date)
        self.command_edit = self.findChild(QLineEdit, "command_edit")
        self.command_edit.setText(self.settings.command)
        self.postpone_spin = self.findChild(QSpinBox, "postpone_spin")
        self.postpone_spin.setValue(int(self.settings.postpone))

        self.time_error = self.findChild(QToolButton, "time_error")
        self.time_error.hide()
        self.date_error = self.findChild(QToolButton, "date_error")
        self.date_error.hide()

        self.popup_check = self.findChild(QCheckBox, "popup_check")
        self.popup_check.setChecked(self.settings.notification)
        self.dialog_check = self.findChild(QCheckBox, "dialog_check")
        self.dialog_check.setChecked(self.settings.dialog)
        self.change_icon_check = self.findChild(QCheckBox, "change_icon_check")
        self.change_icon_check.setChecked(self.settings.indicator_icon)

        self.file_edit = self.findChild(QLineEdit, "file_edit")
        self.file_edit.setText(self.settings.sound_file)
        self.length_spin = self.findChild(QSpinBox, "length_spin")
        self.length_spin.setValue(int(self.settings.sound_length))
        self.loop_check = self.findChild(QCheckBox, "loop_check")
        self.loop_check.setChecked(self.settings.sound_loop)
        self.time_loop_spin = self.findChild(QSpinBox, "time_loop_spin")
        self.time_loop_spin.setValue(self.settings.sound_loop_times)

        self.quick_label_edit = self.findChild(QLineEdit, "quick_label_edit")
        self.quick_label_edit.setText(self.settings.quick_label)
        self.quick_minutes_spin = self.findChild(QSpinBox, "quick_minutes_spin")
        self.quick_minutes_spin.setValue(self.settings.quick_minutes)
        self.quick_slider_check = self.findChild(QCheckBox, "quick_slider_check")
        self.quick_slider_check.setChecked(self.settings.quick_slider)
        self.quick_popup_check = self.findChild(QCheckBox, "quick_popup_check")
        self.quick_popup_check.setChecked(self.settings.quick_popup)
        self.quick_dialog_check = self.findChild(QCheckBox, "quick_dialog_check")
        self.quick_dialog_check.setChecked(self.settings.quick_dialog)
        self.quick_sound_check = self.findChild(QCheckBox, "quick_sound_check")
        self.quick_sound_check.setChecked(self.settings.quick_sound)
        self.quick_info_check = self.findChild(QCheckBox, "quick_info_check")
        self.quick_info_check.setChecked(self.settings.quick_info)

        self.today_color = self.settings.today_color
        self.today_color_rgb = self.info.today_color_rgb
        r = self.today_color_rgb[0]
        g = self.today_color_rgb[1]
        b = self.today_color_rgb[2]
        self.today_button = self.findChild(QPushButton, "today_button")
        self.today_button.setStyleSheet("QPushButton { color:rgb(%d, %d, %d) }" % (r, g, b))
        self.today_button.setText("(%d, %d, %d)" % (r, g, b))

        self.future_color = self.settings.future_color
        self.future_color_rgb = self.info.future_color_rgb
        r = self.future_color_rgb[0]
        g = self.future_color_rgb[1]
        b = self.future_color_rgb[2]
        self.future_button = self.findChild(QPushButton, "future_button")
        self.future_button.setStyleSheet("QPushButton { color:rgb(%d, %d, %d) }" % (r, g, b))
        self.future_button.setText("(%d, %d, %d)" % (r, g, b))

        self.past_color = self.settings.past_color
        self.past_color_rgb = self.info.past_color_rgb
        r = self.past_color_rgb[0]
        g = self.past_color_rgb[1]
        b = self.past_color_rgb[2]
        self.past_button = self.findChild(QPushButton, "past_button")
        self.past_button.setStyleSheet("QPushButton { color:rgb(%d, %d, %d) }" % (r, g, b))
        self.past_button.setText("(%d, %d, %d)" % (r, g, b))

        self.new_check = self.findChild(QCheckBox, "new_check")
        self.new_check.setChecked(self.settings.show_news)
        self.icon_combo = self.findChild(QComboBox, "icon_combo")
        self.icon_combo.setCurrentIndex(self.settings.indicator_icon)
        self.hide_check = self.findChild(QCheckBox, "hide_check")
        self.hide_check.setChecked(self.settings.hide_indicator)

        self.time_format_combo = self.findChild(QComboBox, "time_format_combo")
        self.time_format_combo.setCurrentIndex(self.settings.time_format)
        self.date_format_combo = self.findChild(QComboBox, "date_format_combo")
        self.date_format_combo.setCurrentIndex(self.settings.date_format)

        self.boxcar_email_edit = self.findChild(QLineEdit, "boxcar_email_edit")
        self.boxcar_email_edit.setText(self.boxcar_info.email)
        self.boxcar_notification_check = self.findChild(QCheckBox, "boxcar_notification_check")
        self.boxcar_notification_check.setChecked(self.boxcar_info.default_notify)

    @Slot()
    def on_help_button_pressed(self):
        helpers.show_uri(self, "ghelp:%s" % helpers.get_help_uri('preferences'))

    @Slot()
    def on_time_button_pressed(self):
        simple_time = datetimeutil.str_time_simplify(self.time_edit.text())
        fixed_time = datetimeutil.fix_time_format(simple_time, self.info.time_format_num)

        dialog = TimeDialog(fixed_time, self)
        dialog.update.connect(self.time_updated)
        dialog.exec_()

    @Slot()
    def time_updated(self, time_s):
        self.time_edit.setText(time_s)

    @Slot()
    def on_time_edit_textEdited(self):
        if self.info.valid_time(self.time_edit.text()):
            self.time_error.hide()
        else:
            self.time_error.show()

    @Slot()
    def on_date_button_pressed(self):
        simple_date = datetimeutil.str_date_simplify(self.date_edit.text(), self.info.date_format_num)
        fixed_date = datetimeutil.fix_date_format(simple_date, self.info.date_format_num)

        dialog = DateDialog(fixed_date, self)
        dialog.update.connect(self.date_updated)
        dialog.exec_()

    @Slot()
    def date_updated(self, date_s):
        self.date_edit.setText(date_s)

    @Slot()
    def on_date_edit_textEdited(self):
        if self.info.valid_date(self.date_edit.text()):
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
    def on_file_button_pressed(self):
        pass

    @Slot()
    def on_boxcar_email_button_pressed(self):
        helpers.show_uri(self, "ghelp:%s" % helpers.get_help_uri('services'))

    @Slot()
    def on_today_button_pressed(self):
        old_color = QColor.fromRgb(self.today_color_rgb[0], self.today_color_rgb[1], self.today_color_rgb[2])
        color = QColorDialog.getColor(old_color, self, "Today's Color")
        self.today_color_rgb = color.getRgb()
        self.today_color = rgb_to_hex(self.today_color_rgb)

        r = self.today_color_rgb[0]
        g = self.today_color_rgb[1]
        b = self.today_color_rgb[2]
        self.today_button.setStyleSheet("QPushButton { color:rgb(%d, %d, %d) }" % (r, g, b))
        self.today_button.setText("(%d, %d, %d)" % (r, g, b))

    @Slot()
    def on_future_button_pressed(self):
        old_color = QColor.fromRgb(self.future_color_rgb[0], self.future_color_rgb[1], self.future_color_rgb[2])
        color = QColorDialog.getColor(old_color, self, "Future Color")
        self.future_color_rgb = color.getRgb()
        self.future_color = rgb_to_hex(self.future_color_rgb)

        r = self.future_color_rgb[0]
        g = self.future_color_rgb[1]
        b = self.future_color_rgb[2]
        self.future_button.setStyleSheet("QPushButton { color:rgb(%d, %d, %d) }" % (r, g, b))
        self.future_button.setText("(%d, %d, %d)" % (r, g, b))

    @Slot()
    def on_past_button_pressed(self):
        old_color = QColor.fromRgb(self.past_color_rgb[0], self.past_color_rgb[1], self.past_color_rgb[2])
        color = QColorDialog.getColor(old_color, self, "Past Color")
        self.past_color_rgb = color.getRgb()
        self.past_color = rgb_to_hex(self.past_color_rgb)

        r = self.past_color_rgb[0]
        g = self.past_color_rgb[1]
        b = self.past_color_rgb[2]
        self.past_button.setStyleSheet("QPushButton { color:rgb(%d, %d, %d) }" % (r, g, b))
        self.past_button.setText("(%d, %d, %d)" % (r, g, b))

    @Slot()
    def on_cancel_button_pressed(self):
        self.reject()

    @Slot()
    def on_save_button_pressed(self):
        pass