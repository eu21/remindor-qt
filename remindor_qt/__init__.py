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

import optparse

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-qt')

from PySide.QtCore import *
from PySide.QtGui import *

from remindor_qt import RemindorQtWindow
from remindor_qt.helpers import check_database, check_autostart, log_file, config_dir
from remindor_qt.remindor_qtconfig import get_version
from remindor_qt import resources

from remindor_common.helpers import parse_options, set_up_logging

def main():
    check_autostart()
    check_database()

    (options, parser) = parse_options(get_version())
    set_up_logging("remindor_qt", log_file(), config_dir(), options)

    #Run the application.
    app = QApplication([""])
    app.setWindowIcon(QIcon.fromTheme("remindor-qt"))
    app.setApplicationName("Remindor-Qt")
    app.setApplicationVersion(get_version())
    app.setOrganizationDomain("http://bhdouglass.tk/indicator-remindor/")
    app.setQuitOnLastWindowClosed(False)

    window = RemindorQtWindow.RemindorQtWindow()
    #window.show()

    app.exec_()
