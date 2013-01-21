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

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-qt')

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

import logging
logger = logging.getLogger('remindor_qt')

from remindor_qt.AboutDialog import AboutDialog
from remindor_qt.PreferencesDialog import PreferencesDialog
from remindor_qt.QuickDialog import QuickDialog
from remindor_qt.ReminderDialog import ReminderDialog
from remindor_qt.scheduler_qt import SchedulerQt
from remindor_qt import helpers

from remindor_common.constants import *
from remindor_common.helpers import ManageWindowInfo

class RemindorQtWindow(QMainWindow):
    setup_schedule = True

    def __init__(self, parent = None):
        super(RemindorQtWindow,self).__init__(parent)
        helpers.setup_ui(self, "RemindorQtWindow.ui", True)
        self.resize(700, 300)

        self.reminder_tree = self.findChild(QTreeWidget, "reminder_tree")
        self.reminder_tree.setColumnWidth(0, 200)

        self.tray_menu = QMenu()
        self.tray_menu.addAction(QIcon.fromTheme("add"), "Add", self, SLOT("on_action_add_triggered()"))
        self.tray_menu.addAction(QIcon.fromTheme("media-skip-forward"), "Quick Add", self, SLOT("on_action_quick_add_triggered()"))
        self.tray_menu.addAction(QIcon.fromTheme("media-playback-stop"), "Stop Sound", self, SLOT("on_action_stop_triggered()"))
        self.tray_menu.addAction(QIcon.fromTheme("stock_properties"), "Manage", self, SLOT("show()"))
        self.tray_menu.addAction(QIcon.fromTheme("exit"), "Quit", self, SLOT("close()")) #TODO: change this when reimplementing x-close button

        self.tray_icon = QSystemTrayIcon(QIcon(helpers.get_data_file("media", "remindor-qt-active.svg")), self)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

        self.scheduler = SchedulerQt(self.tray_icon, self.update)
        #self.scheduler.update_signal.connect(self.update)
        self.info = ManageWindowInfo(helpers.database_file())
        self.update()

    @Slot()
    def on_action_add_triggered(self):
        dialog = ReminderDialog(self)
        dialog.show()

    @Slot()
    def on_action_quick_add_triggered(self):
        dialog = QuickDialog(self)
        dialog.added.connect(self.add_to_schedule)
        dialog.show()

    @Slot()
    def on_action_edit_triggered(self):
        dialog = ReminderDialog(self)
        dialog.show()

    @Slot()
    def on_action_postpone_triggered(self):
        pass

    @Slot()
    def on_action_delete_triggered(self):
        pass

    @Slot()
    def on_action_preferences_triggered(self):
        dialog = PreferencesDialog(self)
        dialog.show()

    @Slot()
    def on_action_news_triggered(self):
        helpers.show_uri(self, blogsite)

    @Slot()
    def on_action_help_triggered(self):
        helpers.show_uri(self, "ghelp:%s" % helpers.get_help_uri())

    @Slot()
    def on_action_close_triggered(self):
        self.hide()

    @Slot()
    def on_action_quit_triggered(self):
        self.close()

    @Slot()
    def on_action_refresh_triggered(self):
        pass

    @Slot()
    def on_action_clear_icon_triggered(self):
        self.tray_icon.setIcon(QIcon(get_data_file("media", "remindor-qt-active.svg"))) #TODO: change this based on settings icon

        if self.dbus_service != None:
            logger.debug("emmiting dbus active signal")
            self.dbus_service.emitActive()

    @Slot()
    def on_action_bugs_triggered(self):
        helpers.show_uri(self, bugsite)

    @Slot()
    def on_action_request_triggered(self):
        helpers.show_uri(self, featuresite)

    @Slot()
    def on_action_translate_triggered(self):
        helpers.show_uri(self, translatesite)

    @Slot()
    def on_action_donate_triggered(self):
        helpers.show_uri(self, donatestie)

    @Slot()
    def on_action_ask_triggered(self):
        helpers.show_uri(self, questionsite)

    @Slot()
    def on_action_website_triggered(self):
        helpers.show_uri(self, website)

    @Slot()
    def on_action_about_triggered(self):
        dialog = AboutDialog(self)
        dialog.show()

    @Slot()
    def on_action_stop_triggered(self):
        logger.debug("stopping sound")
        self.scheduler.stop_sound()

        self.on_action_clear_icon_triggered()

    @Slot()
    def add_to_schedule(self, id):
        self.scheduler.add_reminder(id)
        self.update()

    @Slot()
    def update(self):
        logger.debug("update")

        if self.setup_schedule:
            self.info.update(self.scheduler)
            self.setup_schedule = False
        else:
            self.info.update(None)

        if self.info.show_news and self.info.new_news == 1:
            pass
        #    self.news.set_label(_("New News"))
        else:
            pass
        #    self.news.set_label(_("News"))

        if self.info.hide_indicator:
            pass
        #    if self.indicator.get_status() != AppIndicator3.IndicatorStatus.PASSIVE:
        #        self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
        #        logger.debug("setting indicator status to passive: " + str(self.indicator.get_status() == AppIndicator3.IndicatorStatus.PASSIVE))
        else:
            pass
        #    if self.indicator.get_status() != AppIndicator3.IndicatorStatus.ACTIVE:
        #        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        #        logger.debug("setting indicator status to active: " + str(self.indicator.get_status() == AppIndicator3.IndicatorStatus.ACTIVE))

        #iicon = self.indicator.get_icon()
        #if iicon != indicator_icons[settings.indicator_icon]:
        #    self.indicator.set_icon(indicator_icons[settings.indicator_icon])

        logger.debug("update: setting up headers")
        self.reminder_tree.clear()

        self.today = QTreeWidgetItem(self.reminder_tree, [_("Today's Reminders"), "", "", "", ""])
        today_brush = QBrush(Qt.SolidPattern)
        today_brush.setColor(QColor(self.info.today_color[0], self.info.today_color[1], self.info.today_color[2]))
        for i in range(4):
            self.today.setBackground(i, today_brush)
        self.reminder_tree.addTopLevelItem(self.today)

        self.future = QTreeWidgetItem(self.reminder_tree, [_("Future Reminders"), "", "", "", ""])
        future_brush = QBrush(Qt.SolidPattern)
        future_brush.setColor(QColor(self.info.future_color[0], self.info.future_color[1], self.info.future_color[2]))
        for i in range(4):
            self.future.setBackground(i, future_brush)
        self.reminder_tree.addTopLevelItem(self.future)

        self.past = QTreeWidgetItem(self.reminder_tree, [_("Past Reminders"), "", "", "", ""])
        past_brush = QBrush(Qt.SolidPattern)
        past_brush.setColor(QColor(self.info.past_color[0], self.info.past_color[1], self.info.past_color[2]))
        for i in range(4):
            self.past.setBackground(i, past_brush)
        self.reminder_tree.addTopLevelItem(self.past)

        for reminder in self.info.reminder_list:
            parent = self.past
            if reminder.parent == self.info.today:
                parent = self.today
            elif reminder.parent == self.info.future:
                parent = self.future

            temp = QTreeWidgetItem(parent, reminder.qt())
            for i in range(4):
                temp.setToolTip(i, reminder.tooltip)

        self.reminder_tree.expandAll()

        logger.debug("update: done setting up tree")

        return True