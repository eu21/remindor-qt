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
import os
import sys

from remindor_qt.remindor_qtconfig import get_data_file, get_data_path

from remindor_common import database as db

import gettext
from gettext import gettext as _
gettext.textdomain('remindor-qt')

class RTimer(QTimer):
    def __init__(self, interval, slot, id = -1, single_shot = True, start_now = True, parent = None):
        super(RTimer, self).__init__(parent)
        self.setInterval(interval * 1000)
        self.setSingleShot(single_shot)
        self.id = id
        self.slot = slot
        self.start_now = start_now

        if self.id == -1:
            self.timeout.connect(self.slot)
        else:
            self.timeout.connect(self.handler)

        if self.start_now:
            self.start()

    @Slot()
    def handler(self):
        self.slot(self.id)


# Owais Lone : To get quick access to icons and stuff.
def get_media_file(media_file_name):
    media_filename = get_data_file('media', '%s' % (media_file_name,))
    if not os.path.exists(media_filename):
        media_filename = None

    return "file:///" + media_filename

def get_html_file(html_file_name):
    html_filename = get_data_file('html', '%s.html' % (html_file_name,))
    if not os.path.exists(html_filename):
        html_filename = None

    return "file:///" + html_filename

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

def set_up_logging(opts):
    # add a handler to prevent basicConfig
    root = logging.getLogger()
    null_handler = NullHandler()
    root.addHandler(null_handler)

    formatter = logging.Formatter("%(levelname)s:%(name)s: %(funcName)s() '%(message)s'")

    logger = logging.getLogger('remindor_qt')
    logger_sh = logging.StreamHandler()
    logger_sh.setFormatter(formatter)
    logger.addHandler(logger_sh)

    lib_logger = logging.getLogger('remindor_qt_lib')
    lib_logger_sh = logging.StreamHandler()
    lib_logger_sh.setFormatter(formatter)
    lib_logger.addHandler(lib_logger_sh)

    # Set the logging level to show debug messages.
    if opts.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug('logging enabled')
    if opts.verbose > 1:
        lib_logger.setLevel(logging.DEBUG)

def get_help_uri(page = None):
    # help_uri from source tree - default language
    here = os.path.dirname(__file__)
    help_uri = os.path.abspath(os.path.join(here, '..', 'help', 'C'))

    if not os.path.exists(help_uri):
        # installed so use gnome help tree - user's language
        help_uri = 'remindor-qt'

    # unspecified page is the index.page
    if page is not None:
        help_uri = '%s#%s' % (help_uri, page)

    return help_uri

def show_uri(link):
    QDesktopServices.openUrl(QUrl(link, QUrl.TolerantMode))

def show_html_help(page = None):
    show_uri(get_html_file(page))

def alias(alternative_function_name):
    '''see http://www.drdobbs.com/web-development/184406073#l9'''
    def decorator(function):
        '''attach alternative_function_name(s) to function'''
        if not hasattr(function, 'aliases'):
            function.aliases = []
        function.aliases.append(alternative_function_name)
        return function
    return decoratorpass

def get_ui_path():
    return get_data_path() + "/ui/"

def setup_ui(widget, ui, mainwindow = False):
    loader = QUiLoader()
    loader.setWorkingDirectory(QDir(get_ui_path()))

    file = QFile(get_ui_path() + ui)
    file.open(QFile.ReadOnly)

    centralwidget = loader.load(file, widget)
    centralwidget.setWindowFlags(Qt.Widget)
    if mainwindow:
        widget.setCentralWidget(centralwidget)
    else:
        layout = QVBoxLayout()
        layout.addWidget(centralwidget)
        widget.setLayout(layout)

    QMetaObject.connectSlotsByName(widget)
    widget.setWindowTitle(centralwidget.windowTitle())
    widget.setWindowIcon(centralwidget.windowIcon())

def check_autostart():
    if os.name != 'nt':
        #filename = os.getenv('HOME') + '/.config/autostart/remindor-qt.desktop'
        filename = QDesktopServices.storageLocation(QDesktopServices.HomeLocation) + '/.config/autostart/remindor-qt.desktop'

        file_exists = True
        try:
            with open(filename) as f: pass
            #file exists nothing to do
        except IOError:
            #file does not exists create it"""
            file_exists = False

        icon = "remindor-qt"

        #find app path
        app_path = ''
        if getattr(sys, 'frozen', False):
            app_path = sys.executable
        elif __file__:
            app_path = __file__

        #find exec path
        exec_path = 'remindor-qt'
        if '/opt/extras.ubuntu.com' in app_path:
            exec_path = '/opt/extras.ubuntu.com/remindor-qt/bin/remindor-qt'

        exec_exists = False #incase the file gets really messed up
        if file_exists: #make paths correct
            #code from setup.py
            fin = file(filename, 'r')
            fout = file(fin.name + '.new', 'w')

            for line in fin:
                if 'Exec=' in line:
                    line = "Exec=%s\n" % exec_path
                    exec_exists = True
                if 'Icon=' in line:
                    line = "Icon=%s\n" % icon
                fout.write(line)
            fout.flush()
            fout.close()
            fin.close()
            os.rename(fout.name, fin.name)

        if not file_exists or not exec_exists: #create file
            #make directory if needed
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                os.makedirs(directory)

            #create autostart file
            f = open(filename, 'w')
            f.write('[Desktop Entry]\n')
            f.write('Name=Remindor-Qt\n')
            f.write('Comment=Remindor-Qt\n')
            f.write('Categories=GNOME;Utility;\n')
            f.write("Exec=%s\n" % exec_path)
            f.write("Icon=%s\n" % icon)
            f.write('Terminal=false\n')
            f.write('Type=Application\n')
            f.close()
    else:
        print 'not checking autostart, reason: on windows' #TODO: implement this

def config_dir():
    #return os.getenv('HOME') + '/.config/indicator-remindor'
    return QDesktopServices.storageLocation(QDesktopServices.HomeLocation) + '/.config/indicator-remindor'

def database_file():
    return config_dir() + '/indicator-remindor.db'

def log_file():
    return config_dir() + "/remindor-qt.log"

def check_database():
    filename = database_file()
    database = db.Database(filename)
    database.setup()
    database.close()