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

import sys

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
from remindor_common.threads import BlogReader
from remindor_common import database as db

class RemindorQtWindow(QMainWindow):
    setup_schedule = True
    ok_to_close = False

    def __init__(self, parent = None):
        super(RemindorQtWindow,self).__init__(parent)
        helpers.setup_ui(self, "RemindorQtWindow.ui", True)
        self.resize(700, 300)

        self.dbus_service = None

        self.active_icon = QIcon(helpers.get_data_file("media", "remindor-qt-active.svg"))
        self.app_icon = QIcon(helpers.get_data_file("media", "remindor-qt.svg"))
        self.tray_icons = [QIcon.fromTheme("remindor-qt-active", self.active_icon),
                           self.active_icon,
                           QIcon(helpers.get_data_file("media", "remindor-qt-active_dark.svg")),
                           QIcon.fromTheme("remindor-qt", self.app_icon)]

        self.reminder_tree = self.findChild(QTreeWidget, "reminder_tree")
        self.reminder_tree.setColumnWidth(0, 200)
        edit = QAction(QIcon.fromTheme("gtk-edit", QIcon(":/icons/edit.png")), "Edit", self)
        edit.triggered.connect(self.on_action_edit_triggered)
        self.reminder_tree.addAction(edit)
        postpone = QAction(QIcon.fromTheme("go-jump", QIcon(":/icons/postpone.png")), "Postpone", self)
        postpone.triggered.connect(self.on_action_postpone_triggered)
        self.reminder_tree.addAction(postpone)
        delete = QAction(QIcon.fromTheme("edit-delete", QIcon(":/icons/delete.png")), "Delete", self)
        delete.triggered.connect(self.on_action_delete_triggered)
        self.reminder_tree.addAction(delete)

        self.news_action = self.findChild(QAction, "action_news")

        self.tray_menu = QMenu()
        self.tray_menu.addAction(QIcon.fromTheme("add", QIcon(":/icons/add.png")), "Add", self, SLOT("on_action_add_triggered()"))
        self.tray_menu.addAction(QIcon.fromTheme("media-skip-forward", QIcon(":/icons/quick.png")), "Quick Add", self, SLOT("on_action_quick_add_triggered()"))
        self.tray_menu.addAction(QIcon.fromTheme("media-playback-stop", QIcon(":/icons/delete.png")), "Stop Sound", self, SLOT("on_action_stop_triggered()"))
        self.tray_menu.addAction(QIcon.fromTheme("stock_properties", QIcon(":/icons/manage.png")), "Manage", self, SLOT("show()"))
        self.tray_menu.addAction(QIcon.fromTheme("exit", QIcon(":/icons/quit.png")), "Quit", self, SLOT("on_action_quit_triggered()")) #TODO: change this when reimplementing x-close button

        self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("remindor-qt-active", self.active_icon), self)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_activated)

        self.scheduler = SchedulerQt(self.tray_icon, self.update, helpers.database_file())
        self.info = ManageWindowInfo(helpers.database_file())
        self.update()

        b = BlogReader(rssfeed, helpers.database_file())
        b.start()

    @Slot()
    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()
        elif reason == QSystemTrayIcon.MiddleClick:
            self.on_action_add_triggered()

    @Slot()
    def closeEvent(self, event):
        if self.ok_to_close:
            sys.exit(0)
            event.accept()
        else:
            event.ignore()
            self.hide()

    @Slot()
    def on_action_add_triggered(self):
        dialog = ReminderDialog(self)
        dialog.added.connect(self.add_to_schedule)
        dialog.exec_()

    @Slot()
    def on_action_quick_add_triggered(self):
        dialog = QuickDialog(self)
        dialog.added.connect(self.add_to_schedule)
        dialog.exec_()

    @Slot()
    def on_action_edit_triggered(self):
        (selected, is_parent) = self.get_selected()

        if not is_parent:
            dialog = ReminderDialog(self)
            dialog.edit(selected)
            dialog.added.connect(self.add_to_schedule)
            dialog.exec_()

    @Slot()
    def on_action_postpone_triggered(self):
        (selected, is_parent) = self.get_selected()
        if not is_parent:
            self.info.postpone(selected)
            self.update()

    @Slot()
    def on_action_delete_triggered(self):
        (selected, is_parent) = self.get_selected()
        if not is_parent:
            database = db.Database(helpers.database_file())
            database.delete_alarm(selected)
            database.close()

            self.update()

    @Slot()
    def on_action_preferences_triggered(self):
        dialog = PreferencesDialog(self)
        dialog.update.connect(self.update)
        dialog.exec_()

    @Slot()
    def on_action_news_triggered(self):
        helpers.show_uri(self, blogsite)

    @Slot()
    def on_action_help_triggered(self):
        helpers.show_html_help("index")

    @Slot()
    def on_action_close_triggered(self):
        self.hide()

    @Slot()
    def on_action_quit_triggered(self):
        self.ok_to_close = True
        self.close()

    @Slot()
    def on_action_refresh_triggered(self):
        self.update()

    @Slot()
    def on_action_clear_icon_triggered(self):
        self.tray_icon.setIcon(self.tray_icons[self.info.indicator_icon])

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
            self.news_action.setText(_("New News"))
        else:
            self.news_action.setText(_("News"))

        if self.info.hide_indicator:
            if self.tray_icon.isVisible():
                self.tray_icon.hide()
        else:
            if not self.tray_icon.isVisible():
                self.tray_icon.show()

        icon = self.tray_icon.icon()
        icon_name = icon.name()
        if icon_name != "remindor-qt-active" and icon != self.tray_icons[self.info.indicator_icon]:
            self.tray_icon.setIcon(self.tray_icons[self.info.indicator_icon])

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

    def get_selected(self):
        selected_items = self.reminder_tree.selectedItems()
        selected = selected_items[0]

        is_parent = False
        text = selected.text(0)
        if text == self.today.text(0) or text == self.future.text(0) or text == self.past.text(0):
            if selected.text(4) == "": #id is "" only on the 3 parents
                is_parent = True

        if is_parent:
            return -1, is_parent
        else:
            return int(selected.text(4)), is_parent