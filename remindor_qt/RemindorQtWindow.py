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
gettext.textdomain('remindor-common')

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

    def __init__(self, dbus_service = None, parent = None):
        super(RemindorQtWindow,self).__init__(parent)
        self.dbus_service = dbus_service
        helpers.setup_ui(self, "RemindorQtWindow.ui", True)
        self.resize(700, 300)

        self.action_add = self.findChild(QAction, "action_add")
        self.action_quick_add = self.findChild(QAction, "action_quick_add")
        self.action_edit = self.findChild(QAction, "action_edit")
        self.action_postpone = self.findChild(QAction, "action_postpone")
        self.action_delete = self.findChild(QAction, "action_delete")
        self.action_preferences = self.findChild(QAction, "action_preferences")
        self.action_news = self.findChild(QAction, "action_news")
        self.action_help = self.findChild(QAction, "action_help")
        self.action_close = self.findChild(QAction, "action_close")
        self.action_quit = self.findChild(QAction, "action_quit")
        self.action_refresh = self.findChild(QAction, "action_refresh")
        self.action_clear_icon = self.findChild(QAction, "action_clear_icon")
        self.action_bugs = self.findChild(QAction, "action_bugs")
        self.action_request = self.findChild(QAction, "action_request")
        self.action_translate = self.findChild(QAction, "action_translate")
        self.action_donate = self.findChild(QAction, "action_donate")
        self.action_ask = self.findChild(QAction, "action_ask")
        self.action_website = self.findChild(QAction, "action_website")
        self.action_about = self.findChild(QAction, "action_about")
        self.action_stop = self.findChild(QAction, "action_stop")

        self.translate()

        self.info = ManageWindowInfo(helpers.database_file())

        self.active_icon = QIcon(helpers.get_data_file("media", "remindor-qt-active.svg"))
        self.app_icon = QIcon(helpers.get_data_file("media", "remindor-qt.svg"))
        self.tray_icons = [QIcon.fromTheme("remindor-qt-active", self.active_icon),
                           self.active_icon,
                           QIcon(helpers.get_data_file("media", "remindor-qt-active_dark.svg")),
                           QIcon.fromTheme("remindor-qt", self.app_icon)]

        self.reminder_tree = self.findChild(QTreeWidget, "reminder_tree")
        self.reminder_tree.setColumnWidth(0, 200)
        edit = QAction(QIcon.fromTheme("gtk-edit", QIcon(":/icons/edit.png")), _("Edit"), self)
        edit.triggered.connect(self.on_action_edit_triggered)
        self.reminder_tree.addAction(edit)
        postpone = QAction(QIcon.fromTheme("go-jump", QIcon(":/icons/postpone.png")), _("Postpone"), self)
        postpone.triggered.connect(self.on_action_postpone_triggered)
        self.reminder_tree.addAction(postpone)
        delete = QAction(QIcon.fromTheme("edit-delete", QIcon(":/icons/delete.png")), _("Delete"), self)
        delete.triggered.connect(self.on_action_delete_triggered)
        self.reminder_tree.addAction(delete)

        self.news_action = self.findChild(QAction, "action_news")

        self.tray_menu = QMenu()
        self.tray_menu.addAction(QIcon.fromTheme("add", QIcon(":/icons/add.png")), _("Add"), self, SLOT("on_action_add_triggered()"))
        self.tray_menu.addAction(QIcon.fromTheme("media-skip-forward", QIcon(":/icons/quick.png")), _("Quick Add"), self, SLOT("on_action_quick_add_triggered()"))
        self.tray_menu.addAction(QIcon.fromTheme("media-playback-stop", QIcon(":/icons/delete.png")), _("Stop Sound"), self, SLOT("on_action_stop_triggered()"))
        self.tray_menu.addAction(QIcon.fromTheme("stock_properties", QIcon(":/icons/manage.png")), _("Manage"), self, SLOT("show()"))
        self.tray_menu.addAction(QIcon.fromTheme("exit", QIcon(":/icons/quit.png")), _("Quit"), self, SLOT("on_action_quit_triggered()")) #TODO: change this when reimplementing x-close button

        self.tray_icon = QSystemTrayIcon(self.tray_icons[self.info.indicator_icon], self)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_activated)

        self.scheduler = SchedulerQt(self.tray_icon, self.update, helpers.database_file())
        if not self.dbus_service == None:
            self.scheduler.add_dbus_service(self.dbus_service)

        self.update()

        self.updater = QTimer(self)
        self.updater.setInterval(1000 * 60 * 60 * 6) #update everything every 1/4 day
        self.updater.timeout.connect(self.update_schedule)

        b = BlogReader(rssfeed, helpers.database_file())
        b.start()

    def translate(self):
        self.setWindowTitle("Manage Reminders")

        self.action_add.setText(_("Add"))
        self.action_quick_add.setText(_("Quick Add"))
        self.action_edit.setText(_("Edit"))
        self.action_postpone.setText(_("Postpone"))
        self.action_delete.setText(_("Delete"))
        self.action_preferences.setText(_("Preferences"))
        self.action_news.setText(_("News"))
        self.action_help.setText(_("Help"))
        self.action_close.setText(_("Close"))
        self.action_quit.setText(_("Quit"))
        self.action_refresh.setText(_("Refresh"))
        self.action_clear_icon.setText(_("Clear Icon"))
        self.action_bugs.setText(_("Submit Bugs"))
        self.action_request.setText(_("Request Feature"))
        self.action_translate.setText(_("Help Translate"))
        self.action_donate.setText(_("Donate"))
        self.action_ask.setText(_("Ask a Question"))
        self.action_website.setText(_("Website"))
        self.action_about.setText(_("About"))
        self.action_stop.setText(_("Stop Sound"))

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
            if self.info.postpone(selected):
                message = _("Sorry, you cannot postpone a repeating time.")
                QMessageBox.information(self, _("Postpone"), message, QMessageBox.Ok)

            self.update()

    @Slot()
    def on_action_delete_triggered(self):
        (selected, is_parent) = self.get_selected()
        if not is_parent:
            self.info.delete(selected)

            self.update()

    @Slot()
    def on_action_preferences_triggered(self):
        dialog = PreferencesDialog(self)
        dialog.update.connect(self.update)
        dialog.exec_()

    @Slot()
    def on_action_news_triggered(self):
        self.news_action.setText(_("News"))
        helpers.show_uri(blogsite)

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
        self.update_schedule()

    @Slot()
    def on_action_clear_icon_triggered(self):
        self.tray_icon.setIcon(self.tray_icons[self.info.indicator_icon])

        if self.dbus_service != None:
            logger.debug("emmiting dbus active signal")
            self.dbus_service.emitActive()

    @Slot()
    def on_action_bugs_triggered(self):
        helpers.show_uri(bugsite_qt)

    @Slot()
    def on_action_request_triggered(self):
        helpers.show_uri(featuresite_qt)

    @Slot()
    def on_action_translate_triggered(self):
        helpers.show_uri(translatesite)

    @Slot()
    def on_action_donate_triggered(self):
        helpers.show_uri(donatesite)

    @Slot()
    def on_action_ask_triggered(self):
        helpers.show_uri(questionsite_qt)

    @Slot()
    def on_action_website_triggered(self):
        helpers.show_uri(website)

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

        if self.info.show_news == 1 and self.info.new_news == 1:
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
        if icon_name != "remindor-qt-active":
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

    @Slot()
    def update_schedule(self):
        self.setup_schedule = True
        self.scheduler.clear_schedule()

        logger.debug("updating the whole schedule")
        self.update()
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

    def dbus_receiver(self, command):
        logger.debug("received " + command + " signal from dbus")

        if command == "update":
            self.update_schedule()
        elif command == "stop":
            logger.debug("dbus: stopping sound...")
            self.on_action_stop_triggered()
        elif command == "manage":
            self.show()
        elif command == "close":
            self.ok_to_close = True
            self.close()
        elif command == "attention" or command == "active":
            pass #don't do anything, we probably sent this signal
        else:
            logger.debug("unrecognized dbus command: " + command)