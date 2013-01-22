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
from PySide.QtSvg import *

from remindor_qt.helpers import RTimer, get_data_file
from remindor_common.scheduler import GenericScheduler

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-qt')

import logging
logger = logging.getLogger('remindor_qt')

class SchedulerQtHelper(QObject):
    update_signal = Signal()

    def __init__(self, slot):
        QObject.__init__(self)
        self.slot = slot
        self.update_signal.connect(slot)

    def update(self):
        self.update_signal.emit()

class SchedulerQt(GenericScheduler):
    def __init__(self, tray_icon, slot):
        GenericScheduler.__init__(self)
        self.tray_icon = tray_icon
        self.helper = SchedulerQtHelper(slot)

    def remove_reminder(self, reminder):
        logger.debug("schedulerqt: remove_reminder")
        reminder.stop()

    def change_icon(self):
        logger.debug("schedulerqt: change_icon")
        self.tray_icon.setIcon(QIcon.fromTheme("remindor-qt-active"))

        if self.dbus_service != None:
            logger.debug("emmiting dbus attention signal")
            self.dbus_service.emitAttention()

    def remove_playing_sound(self):
        logger.debug("schedulerqt: remove_playing_sound")
        self.playing_sound.stop()

    def add_playing_sound(self, length):
        logger.debug("schedulerqt: add_playing_sound")
        self.playing_sound = RTimer(int(length), self.stop_sound)

    def popup_notification(self, label, notes):
        logger.debug("schedulerqt: popup_notification: " + label + " " + notes)
        self.tray_icon.showMessage(label, notes) #TODO: maybe use pynotify?

    def popup_dialog(self, label, notes):
        logger.debug("schedulergtk: popup_dialog: " + label + " " + notes)

        dialog = QMessageBox(QMessageBox.Information, label, notes, QMessageBox.Close, self)
        dialog.setIconPixmap(QPixmap(get_data_file("media", "remindor-qt.png")))
        dialog.show()

    def update_schedule(self):
        logger.debug("schedulerqt: update_schedule")
        self.helper.update()

    def add_to_schedule(self, delay, id):
        logger.debug("schedulerqt: add_to_schedule, delay: " + str(delay))
        self.schedule.append(RTimer(int(delay), self.run_alarm, id))