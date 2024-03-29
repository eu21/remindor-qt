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
gettext.textdomain('remindor-common')

use_dbus = True
try:
    import dbus
except:
    use_dbus = False

from remindor_qt import helpers
from remindor_qt.remindor_qtconfig import get_data_file
from remindor_qt.CommandDialog import CommandDialog
from remindor_qt.DateDialog import DateDialog
from remindor_qt.TimeDialog import TimeDialog

from remindor_common.helpers import rgb_to_hex, PreferencesDialogInfo, valid_date, valid_time, is_string
from remindor_common import datetimeutil

class PreferencesDialog(QDialog):
    update = Signal()
    pushbullet_valid = ''

    def __init__(self, parent = None):
        super(PreferencesDialog, self).__init__(parent)
        helpers.setup_ui(self, "PreferencesDialog.ui")
        self.info = PreferencesDialogInfo(helpers.database_file())
        self.settings = self.info.settings
        self.boxcar_original = self.settings.boxcar_token

        self.stack_widget = self.findChild(QStackedWidget, "stack")
        self.list_widget = self.findChild(QListWidget, "list")

        self.label_label = self.findChild(QLabel, "label_label")
        self.time_label = self.findChild(QLabel, "time_label")
        self.date_label = self.findChild(QLabel, "date_label")
        self.command_label = self.findChild(QLabel, "command_label")
        self.postpone_label = self.findChild(QLabel, "postpone_label")

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

        self.time_button = self.findChild(QPushButton, "time_button")
        self.date_button = self.findChild(QPushButton, "date_button")
        self.command_button = self.findChild(QPushButton, "command_button")

        self.time_error = self.findChild(QToolButton, "time_error")
        self.time_error.hide()
        self.date_error = self.findChild(QToolButton, "date_error")
        self.date_error.hide()

        self.popup_label = self.findChild(QLabel, "popup_label")
        self.dialog_label = self.findChild(QLabel, "dialog_label")
        self.change_icon_label = self.findChild(QLabel, "change_icon_label")

        self.popup_check = self.findChild(QCheckBox, "popup_check")
        self.popup_check.setChecked(self.settings.popup)
        self.dialog_check = self.findChild(QCheckBox, "dialog_check")
        self.dialog_check.setChecked(self.settings.dialog)
        self.change_icon_check = self.findChild(QCheckBox, "change_icon_check")
        self.change_icon_check.setChecked(self.settings.change_indicator)

        self.file_label = self.findChild(QLabel, "sound_label")
        self.length_label = self.findChild(QLabel, "length_label")
        self.length_label2 = self.findChild(QLabel, "length_label2")
        self.loop_label = self.findChild(QLabel, "loop_label")
        self.time_loop_label = self.findChild(QLabel, "time_loop_label")

        self.file_edit = self.findChild(QLineEdit, "file_edit")
        self.file_edit.setText(self.settings.sound_file)
        self.length_spin = self.findChild(QSpinBox, "length_spin")
        self.length_spin.setValue(int(self.settings.sound_play_length))
        self.loop_check = self.findChild(QCheckBox, "loop_check")
        self.loop_check.setChecked(self.settings.sound_loop)
        self.time_loop_spin = self.findChild(QSpinBox, "time_loop_spin")
        self.time_loop_spin.setValue(self.settings.sound_loop_times)

        self.quick_label_label = self.findChild(QLabel, "quick_label_label")
        self.quick_minutes_label = self.findChild(QLabel, "quick_minutes_label")
        self.quick_unit_label = self.findChild(QLabel, "quick_unit_label")
        self.quick_slider_label = self.findChild(QLabel, "quick_slider_label")
        self.quick_popup_label = self.findChild(QLabel, "quick_popup_label")
        self.quick_dialog_label = self.findChild(QLabel, "quick_dialog_label")
        self.quick_sound_label = self.findChild(QLabel, "quick_sound_label")
        self.quick_info_label = self.findChild(QLabel, "quick_info_label")

        self.quick_label_edit = self.findChild(QLineEdit, "quick_label_edit")
        self.quick_label_edit.setText(self.settings.quick_label)
        self.quick_minutes_spin = self.findChild(QSpinBox, "quick_minutes_spin")
        self.quick_minutes_spin.setValue(self.settings.quick_minutes)
        self.quick_unit_combo = self.findChild(QComboBox, "quick_unit_combo")
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

        self.simple_popup_label = self.findChild(QLabel, "simple_popup_label")
        self.simple_dialog_label = self.findChild(QLabel, "simple_dialog_label")
        self.simple_sound_label = self.findChild(QLabel, "simple_sound_label")

        self.simple_popup_check = self.findChild(QCheckBox, "simple_popup_check")
        self.simple_popup_check.setChecked(self.settings.simple_popup)
        self.simple_dialog_check = self.findChild(QCheckBox, "simple_dialog_check")
        self.simple_dialog_check.setChecked(self.settings.simple_dialog)
        self.simple_sound_check = self.findChild(QCheckBox, "simple_sound_check")
        self.simple_sound_check.setChecked(self.settings.simple_sound)

        self.today_label = self.findChild(QLabel, "today_label")
        self.future_label = self.findChild(QLabel, "future_label")
        self.past_label = self.findChild(QLabel, "past_label")
        self.new_label = self.findChild(QLabel, "new_label")
        self.icon_label = self.findChild(QLabel, "icon_label")
        self.hide_label = self.findChild(QLabel, "hide_label")

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
        self.hide_check = self.findChild(QCheckBox, "hide_check")
        self.hide_check.setChecked(self.settings.hide_indicator)
        self.hide_start = self.settings.hide_indicator

        if not use_dbus:
            self.hide_check.setChecked(False)
            self.hide_check.setDisabled(True)
            self.hide_label.setDisabled(True)

        self.time_format_label = self.findChild(QLabel, "time_format_label")
        self.date_format_label = self.findChild(QLabel, "date_format_label")

        self.time_format_combo = self.findChild(QComboBox, "time_format_combo")
        self.date_format_combo = self.findChild(QComboBox, "date_format_combo")

        self.boxcar_token_button = self.findChild(QCommandLinkButton, "boxcar_token_button")
        self.boxcar_notification_label = self.findChild(QLabel, "boxcar_notification_label")

        self.boxcar_token_edit = self.findChild(QLineEdit, "boxcar_token_edit")
        self.boxcar_token_edit.setText(self.settings.boxcar_token)
        self.boxcar_notification_check = self.findChild(QCheckBox, "boxcar_notification_check")
        self.boxcar_notification_check.setChecked(self.settings.boxcar_notify)

        self.pushbullet_button = self.findChild(QCommandLinkButton, 'pushbullet_button')
        self.pushbullet_device_label = self.findChild(QLabel, 'pushbullet_device_label')

        self.pushbullet_api_key_edit = self.findChild(QLineEdit, 'pushbullet_api_key_edit')
        self.pushbullet_api_key_edit.setText(self.settings.pushbullet_api_key)
        self.pushbullet_device_edit = self.findChild(QComboBox, 'pushbullet_device_edit')
        self.pushbullet_refresh = self.findChild(QPushButton, 'pushbullet_refresh')
        self.refresh_pushbullet_combobox(self.settings.pushbullet_devices)
        self.pushbullet_valid = self.settings.pushbullet_api_key

        self.help_button = self.findChild(QPushButton, "help_button")
        self.cancel_button = self.findChild(QPushButton, "cancel_button")
        self.save_button = self.findChild(QPushButton, "save_button")

        self.translate()

        self.icon_combo.setCurrentIndex(self.settings.indicator_icon)
        self.time_format_combo.setCurrentIndex(self.settings.time_format)
        self.date_format_combo.setCurrentIndex(self.settings.date_format)
        self.quick_unit_combo.setCurrentIndex(self.settings.quick_unit)

    def translate(self):
        self.setWindowTitle(_("Preferences"))

        tabs = [
            _("Standard Reminders"),
            _("Notifications"),
            _("Sound"),
            _("Quick Reminders"),
            _("Simple Reminders"),
            _("Interface"),
            _("Format"),
            _("Services")
        ]

        self.list_widget.clear()
        self.list_widget.addItems(tabs)

        self.label_label.setText(_("Default Label"))
        self.time_label.setText(_("Default Time"))
        self.date_label.setText(_("Default Date"))
        self.command_label.setText(_("Default Command"))
        self.postpone_label.setText(_("Minutes to Postpone"))

        self.time_button.setText(_("Edit"))
        self.date_button.setText(_("Edit"))
        self.command_button.setText(_("Edit"))

        self.popup_label.setText(_("Popup"))
        self.dialog_label.setText(_("Dialog"))
        self.change_icon_label.setText(_("Change Tray\nIcon on Reminder"))

        self.file_label.setText(_("Default Sound File"))
        self.length_label.setText(_("Default Play Length"))
        self.length_label2.setText(_("s (0 for end)"))
        self.loop_label.setText(_("Loop Sound"))
        self.time_loop_label.setText(_("Times to Loop"))

        self.quick_label_label.setText(_("Default Quick Label"))
        self.quick_minutes_label.setText(_("Default Quick Time"))
        self.quick_unit_label.setText(_("Default Quick Unit"))
        self.quick_slider_label.setText(_("Use Slider"))
        self.quick_popup_label.setText(_("Popup Notification"))
        self.quick_dialog_label.setText(_("Dialog Notification"))
        self.quick_sound_label.setText(_("Use standard reminder\nsound settings"))
        self.quick_info_label.setText(_("Show info on dialog"))

        units = [
            _("minute(s)"),
            _("hour(s)"),
            _("days(s)")
        ]

        self.quick_unit_combo.clear()
        self.quick_unit_combo.addItems(units)

        self.simple_popup_label.setText(_("Popup Notification"))
        self.simple_dialog_label.setText(_("Dialog Notification"))
        self.simple_sound_label.setText(_("Use standard reminder\nsound settings"))

        self.today_label.setText(_("Today's Reminder Color"))
        self.future_label.setText(_("Future Reminder Color"))
        self.past_label.setText(_("Past Reminder Color"))
        self.new_label.setText(_("Show News\nNotifications"))
        self.icon_label.setText(_("Tray Icon"))
        self.hide_label.setText(_("Hide Tray Icon"))

        icons = [
            _("System Theme"),
            _("Light Icon"),
            _("Dark Icon"),
            _("App Icon")
        ]

        self.icon_combo.clear()
        self.icon_combo.addItems(icons)

        self.time_format_label.setText(_("Time Format"))
        self.date_format_label.setText(_("Date Format"))

        self.boxcar_token_button.setText(_("Boxcar Token"))
        self.boxcar_notification_label.setText(_("Boxcar Notification"))

        self.pushbullet_button.setText(_('Pushbullet Api Key'))
        self.pushbullet_device_label.setText(_('Pushbullet\nDefault Device'))
        self.pushbullet_refresh.setText(_('Refresh'))

        self.help_button.setText(_("Help"))
        self.cancel_button.setText(_("Cancel"))
        self.save_button.setText(_("Save"))

    @Slot()
    def on_help_button_pressed(self):
        helpers.show_html_help("preferences")

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
        if valid_time(self.time_edit.text()):
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
        if valid_date(self.date_edit.text(), self.settings.date_format):
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
        caption = _("Choose Sound")
        sound_dir = get_data_file('media', 'sounds')
        file_filter = _("Sounds (*.mp3 *.ogg *.wav);;MP3 (*.mp3);;Ogg (*.ogg);;WAVE (*.wav)")

        (filename, selected_filter) = QFileDialog.getOpenFileName(self, caption, sound_dir, file_filter)
        self.file_edit.setText(filename)

    @Slot()
    def on_boxcar_token_button_pressed(self):
        helpers.show_html_help("services")

    @Slot()
    def on_pushbullet_button_pressed(self):
        helpers.show_html_help('services')

    @Slot()
    def on_pushbullet_refresh_pressed(self):
        if self.pushbullet_api_key_edit.text() == '':
            message = _('Please provide a Pushbullet api key.')
            QMessageBox.information(self, 'Pushbullet', message)
        else:
            self.validate_pushbullet()
            self.refresh_pushbullet_combobox(self.settings.pushbullet_devices)

    def validate_pushbullet(self):
        value = True
        if self.pushbullet_valid != self.pushbullet_api_key_edit.text():
            if self.pushbullet_api_key_edit.text() == '':
                self.settings.pushbullet_devices = []
                self.settings.pushbullet_api_key = ''
                value = True
            else:
                value = self.info.refresh_pushbullet_devices(self.pushbullet_api_key_edit.text())
                if is_string(value):
                    self.pushbullet_valid = ''

                    message = ''
                    if value == self.info.pushbullet_invalid:
                        message = _('The api key you provided is invalid.\nPlease check your account on pushbullet.com.')
                        self.settings.pushbullet_devices = []
                        self.settings.pushbullet_api_key = ''
                    elif value == self.info.pushbullet_error:
                        message = _('There was an error connecting with Pushbullet.\nPlease check your api key or network connection.')
                    elif value == self.info.pushbullet_retry:
                        message = _('There was an error connecting with Pushbullet.\nPlease try again later.')
                    elif value == self.info.pushbullet_delete:
                        self.settings.pushbullet_devices = []
                        self.settings.pushbullet_api_key = ''

                    if message != '':
                        QMessageBox.information(self, 'Pushbullet', message)

                    value = False
                else:
                    self.pushbullet_valid = self.pushbullet_api_key_edit.text()
                    self.settings.pushbullet_devices = value
                    self.settings.pushbullet_api_key = self.pushbullet_api_key_edit.text()
                    value = True

        return value

    def refresh_pushbullet_combobox(self, devices = []):
        devices = list(devices)
        devices.insert(0, {'id': -1, 'name': _('None')})

        self.pushbullet_device_edit.clear()
        for device in devices:
            self.pushbullet_device_edit.addItem(device['name'])

        self.pushbullet_device_edit.setCurrentIndex(self.info.pushbullet_device_index)

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
        self.settings.label = self.label_edit.text()
        self.settings.time = self.time_edit.text()
        self.settings.date = self.date_edit.text()
        self.settings.command = self.command_edit.text()
        self.settings.postpone = self.postpone_spin.value()

        self.settings.popup = self.popup_check.isChecked()
        self.settings.dialog = self.dialog_check.isChecked()
        self.settings.change_indicator = self.change_icon_check.isChecked()

        self.settings.sound_file = self.file_edit.text()
        self.settings.sound_play_length = self.length_spin.value()
        self.settings.sound_loop = self.loop_check.isChecked()
        self.settings.sound_loop_times = self.time_loop_spin.value()

        self.settings.quick_label = self.quick_label_edit.text()
        self.settings.quick_minutes = self.quick_minutes_spin.value()
        self.settings.quick_unit = self.quick_unit_combo.currentIndex()
        self.settings.quick_slider = self.quick_slider_check.isChecked()
        self.settings.quick_popup = self.quick_popup_check.isChecked()
        self.settings.quick_dialog = self.quick_dialog_check.isChecked()
        self.settings.quick_sound = self.quick_sound_check.isChecked()
        self.settings.quick_info = self.quick_info_check.isChecked()

        self.settings.simple_popup = self.simple_popup_check.isChecked()
        self.settings.simple_dialog = self.simple_dialog_check.isChecked()
        self.settings.simple_sound = self.simple_sound_check.isChecked()

        self.settings.today_color = self.today_color
        self.settings.future_color = self.future_color
        self.settings.past_color = self.past_color
        self.settings.show_news = self.new_check.isChecked()
        self.settings.indicator_icon = self.icon_combo.currentIndex()
        self.settings.hide_indicator = self.hide_check.isChecked()

        self.settings.time_format = self.time_format_combo.currentIndex()
        self.settings.date_format = self.date_format_combo.currentIndex()

        self.settings.boxcar_token = self.boxcar_token_edit.text()
        self.settings.boxcar_notify = self.boxcar_notification_check.isChecked()

        pushbullet_ok = self.validate_pushbullet()
        if pushbullet_ok:
            self.settings.pushbullet_device = self.info.get_pushbullet_id(self.pushbullet_device_edit.currentIndex(), self.settings.pushbullet_devices)

        ok = True
        '''
        status = self.info.validate_boxcar(boxcar_email, boxcar_notify, self.boxcar_original)
        if status == self.info.boxcar_add:
            self.settings.boxcar_email = boxcar_email
            self.settings.boxcar_notify = boxcar_notify
        elif status == self.info.boxcar_delete:
            self.settings.boxcar_email = ""
            self.settings.boxcar_notify = False
        elif status == self.info.boxcar_subscribe:
            message = _("It seems that you are not yet signed up for Boxcar.\nPlease visit boxcar.io to signup.")
            QMessageBox.information(self, "Boxcar", message)
            ok = False
        else:
            message = _("There has been a error connecting with Boxcar,\nplease check your email address or network connection.")
            QMessageBox.critical(self, "Boxcar", message)
            ok = False
        '''

        if ok and self.settings.hide_indicator and not self.hide_start:
            message = _("You have chosen to hide the indicator.\nOnly use this option if you know what you are doing!\n\nYou can run the command \"%s -p\"\nfrom the command line to open the preferences dialog\nto change this option.\n\nWould you like to continue?") % "remindor-qt"
            ans = QMessageBox.question(self, _("Important!"), message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ans == QMessageBox.No:
                ok = False

        if ok and pushbullet_ok:
            value = self.info.preferences(self.settings)
            if value == self.info.time_error:
                self.time_error.show()
                self.stack_widget.setCurrentIndex(0)
                self.list_widget.setCurrentRow(0)
                self.time_edit.setFocus()
            elif value == self.info.date_error:
                self.date_error.show()
                self.stack_widget.setCurrentIndex(0)
                self.list_widget.setCurrentRow(0)
                self.date_edit.setFocus()
            elif value == self.info.ok:
                self.update.emit()
                self.accept()
