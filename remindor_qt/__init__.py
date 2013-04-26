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

import optparse, sys, os

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-common')

import PySide
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtSvg

use_dbus = True
try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    from remindor_common.dbus_service import dbus_service
except:
    use_dbus = False

from remindor_qt import RemindorQtWindow
from remindor_qt.PreferencesDialog import PreferencesDialog
from remindor_qt.QuickDialog import QuickDialog
from remindor_qt.ReminderDialog import ReminderDialog
from remindor_qt.helpers import check_database, check_autostart, log_file, config_dir
from remindor_qt.remindor_qtconfig import get_version
from remindor_qt import resources

from remindor_common.helpers import parse_options, set_up_logging

def main():
    check_autostart()
    check_database()

    (options, parser) = parse_options(get_version())
    set_up_logging("remindor_qt", log_file(), config_dir(), options)

    import logging
    logger = logging.getLogger('remindor_qt')

    #Run the application.
    app = QApplication([""])
    app.setWindowIcon(QIcon.fromTheme("remindor-qt"))
    app.setApplicationName("Remindor-Qt")
    app.setApplicationVersion(get_version())
    app.setOrganizationDomain("http://bhdouglass.tk/indicator-remindor/")
    app.setQuitOnLastWindowClosed(False)

    if os.name == 'nt':
        for plugins_dir in [os.path.join(p, 'plugins') for p in PySide.__path__]:
            qApp.addLibraryPath(plugins_dir)

    QTextCodec.setCodecForCStrings(QTextCodec.codecForName("UTF-8"))

    if use_dbus:
        DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus()
        ds = dbus_service(session_bus)

        if options.add:
            dialog = ReminderDialog(None)
            dialog.exec_()

            ds.emitUpdate()
            sys.exit(0)

        elif options.quick:
            dialog = QuickDialog(None)
            dialog.exec_()

            ds.emitUpdate()
            sys.exit(0)

        elif options.manage:
            ds.emitManage()
            sys.exit(0)

        elif options.prefs:
            dialog = PreferencesDialog(None)
            dialog.exec_()

            ds.emitUpdate()
            sys.exit(0)

        elif options.stop:
            ds.emitStop()
            sys.exit(0)

        elif options.update:
            ds.emitUpdate()
            sys.exit(0)

        elif options.close:
            ds.emitClose()
            sys.exit(0)

        else:
            window = RemindorQtWindow.RemindorQtWindow(ds)

            bus = dbus.SystemBus()
            bus.add_signal_receiver(window.update_schedule, signal_name='Resuming',
                dbus_interface='org.freedesktop.UPower', path='/org/freedesktop/UPower')

            bus2 = dbus.SessionBus()
            bus2.add_signal_receiver(window.dbus_receiver, signal_name=None,
                dbus_interface=ds.interface(), path=ds.path())
    else:
        logger.debug('Unable to initialize dbus, this features will be disabled')

        if options.add or options.quick or options.manage or options.prefs or options.stop or options.update or options.close:
            logger.warn('dbus is not available, command line options are disabled')
            print 'dbus is not available, command line options are disabled'
            sys.exit(0)
        else:
            window = RemindorQtWindow.RemindorQtWindow()

    app.exec_()
