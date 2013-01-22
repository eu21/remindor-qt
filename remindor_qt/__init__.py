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

import optparse

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-qt')

from PySide.QtCore import *
from PySide.QtGui import *

from remindor_qt import RemindorQtWindow
from remindor_qt.helpers import set_up_logging, check_database, check_autostart
from remindor_qt.remindor_qtconfig import get_version

def parse_options():
    parser = optparse.OptionParser(version="%%prog %s" % get_version())
    parser.add_option(
        "-v", "--verbose", action="count", dest="verbose",
        help=_("Show debug messages (-vv debugs remindor_common also)"))
    (options, args) = parser.parse_args()

    set_up_logging(options)

def main():
    check_autostart()
    check_database()
    parse_options()

    # Run the application.
    app = QApplication([""])
    window = RemindorQtWindow.RemindorQtWindow()
    window.show()
    app.exec_()