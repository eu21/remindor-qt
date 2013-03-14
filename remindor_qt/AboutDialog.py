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

from remindor_qt import helpers
from remindor_qt.remindor_qtconfig import get_version

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-common')

class AboutDialog(QDialog):
    def __init__(self, parent = None):
        super(AboutDialog, self).__init__(parent)
        helpers.setup_ui(self, "AboutDialog.ui")

        self.license_label = self.findChild(QLabel, "license_label")
        self.version_label = self.findChild(QLabel, "version_label")
        self.version_label.setText(get_version())

        self.credits_button = self.findChild(QPushButton, "credits_button")
        self.close_button = self.findChild(QPushButton, "close_button")

        self.translate()

    def translate(self):
        self.setWindowTitle(_("About Remindor-Qt"))
        self.license_label.setText(_("License: GPL-3"))
        self.credits_button.setText(_("Credits"))
        self.close_button.setText(_("Close"))

    @Slot()
    def on_close_button_pressed(self):
        self.close()

    @Slot()
    def on_credits_button_pressed(self):
        message = _("Author: Brian Douglass\n\nTranslators:\nJan Schürmann (German)\nA.J. Baudrez (Dutch)\nPastor (Polish)\nasensio (Portuguese)")
        QMessageBox.information(self, _("Credits"), message, QMessageBox.Close)