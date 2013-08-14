#!/usr/bin/env python
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

import os
import sys

use_py2exe = True
try:
    import py2exe
except:
    use_py2exe = False

try:
    import DistUtilsExtra.auto
except ImportError:
    print >> sys.stderr, 'To build remindor-qt you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)
assert DistUtilsExtra.auto.__version__ >= '2.18', 'needs DistUtilsExtra.auto >= 2.18'

def update_config(values = {}):

    oldvalues = {}
    try:
        fin = file('remindor_qt/remindor_qtconfig.py', 'r')
        fout = file(fin.name + '.new', 'w')

        for line in fin:
            fields = line.split(' = ') # Separate variable from value
            if fields[0] in values:
                oldvalues[fields[0]] = fields[1].strip()
                line = "%s = %s\n" % (fields[0], values[fields[0]])
            fout.write(line)
            
        fout.flush()
        fout.close()
        fin.close()
        os.rename(fin.name, fin.name + '.old')
        os.rename(fout.name, fin.name)
        os.remove(fin.name + '.old')
    except (OSError, IOError), e:
        print ("ERROR: Can't find remindor_qt/remindor_qtconfig.py")
        sys.exit(1)
    return oldvalues

class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    def run(self):
        data_dir = self.prefix + '/share/remindor-qt/'
        if os.name == 'nt' and use_py2exe:
            data_dir = '../../share/remindor-qt/'
    
        values = {'__remindor_qt_data_directory__': "'%s'" % (data_dir),
                  '__version__': "'%s'" % self.distribution.get_version()}
        previous_values = update_config(values)
        DistUtilsExtra.auto.install_auto.run(self)
        update_config(previous_values)

data_files = []
packages = []
if os.name != 'nt':
	packages = ['remindor_qt']

    data_files = [
        ('/usr/share/icons/hicolor/16x16/apps/', ['data/media/hicolor/16x16/apps/remindor-qt.png']),
        ('/usr/share/icons/hicolor/22x22/apps/', ['data/media/hicolor/22x22/apps/remindor-qt.png']),
        ('/usr/share/icons/hicolor/24x24/apps/', ['data/media/hicolor/24x24/apps/remindor-qt.png']),
        ('/usr/share/icons/hicolor/32x32/apps/', ['data/media/hicolor/32x32/apps/remindor-qt.png']),
        ('/usr/share/icons/hicolor/36x36/apps/', ['data/media/hicolor/36x36/apps/remindor-qt.png']),
        ('/usr/share/icons/hicolor/48x48/apps/', ['data/media/hicolor/48x48/apps/remindor-qt.png']),
        ('/usr/share/icons/hicolor/64x64/apps/', ['data/media/hicolor/64x64/apps/remindor-qt.png']),
        ('/usr/share/icons/hicolor/72x72/apps/', ['data/media/hicolor/72x72/apps/remindor-qt.png']),
        ('/usr/share/icons/hicolor/scalable/apps/', ['data/media/hicolor/scalable/apps/remindor-qt.svg']),
        ('/usr/share/icons/hicolor/scalable/status/', ['data/media/hicolor/scalable/status/remindor-qt-active.svg']),
        ('/usr/share/icons/hicolor/scalable/status/', ['data/media/hicolor/scalable/status/remindor-qt-attention.svg']),
        ('/usr/share/icons/hicolor/scalable/status/', ['data/media/hicolor/scalable/status/remindor-qt-error.svg']),
        ('/usr/share/icons/ubuntu-mono-light/status/16/', ['data/media/ubuntu-mono-light/status/16/remindor-qt-active.svg']),
        ('/usr/share/icons/ubuntu-mono-light/status/22/', ['data/media/ubuntu-mono-light/status/22/remindor-qt-active.svg']),
        ('/usr/share/icons/ubuntu-mono-light/status/24/', ['data/media/ubuntu-mono-light/status/24/remindor-qt-active.svg']),
        ('/usr/share/icons/Faenza/apps/scalable/', ['data/media/Faenza/apps/scalable/remindor-qt.svg']),
        ('/usr/share/icons/Faenza/status/scalable/', ['data/media/Faenza/status/scalable/remindor-qt-active.svg']),
        ('/usr/share/icons/Faenza/status/scalable/', ['data/media/Faenza/status/scalable/remindor-qt-attention.svg']),
        ('/usr/share/icons/Faenza/status/scalable/', ['data/media/Faenza/status/scalable/remindor-qt-error.svg']),
        ('/usr/share/icons/Mint-X/status/scalable/', ['data/media/Mint-X/status/scalable/remindor-qt-active.svg']),
        ('/usr/share/icons/Mint-X-Dark/status/scalable/', ['data/media/Mint-X-Dark/status/scalable/remindor-qt-active.svg'])
    ]
else:
	packages = ['remindor_qt', 'remindor_common']

    for item in os.walk('data'):
        path = item[0].replace('data/', 'share/remindor-qt/')
        path = item[0].replace('data\\', 'share\\remindor-qt\\')
        if item[2]:
            files = []
            for f in item[2]:
                files.append(item[0] + '/' + f)

            data_files.append((path, files))

DistUtilsExtra.auto.setup(
    name = 'remindor-qt',
    version = '13.08',
    license = 'GPL-3',
    author = 'Brian Douglass',
    author_email = 'bhdouglass@gmail.com',
    description = 'Schedule reminders easily from a tray icon',
    url = 'http://bhdouglass.tk/remindor/qt/',
    long_description = 'Remindor-Qt is an system tray app that allows you to schedule reminders.  A reminder can be configured to show a notification, play a sound, and/or run a command.  Reminders can be scheduled on one day or they can be set to repeat every day, every monday, every 30 days, etc.  They can also be set to repeat minutely or hourly.',
    cmdclass = {'install': InstallAndUpdateDataDirectory},
    data_files = data_files,
    packages = packages,
    console = ['remindor_qt.py'],
    options = {'py2exe': {'includes': ['feedparser']}},
    windows = [{'script': 'remindor_qt.py', 'icon_resources': [(1, 'data/media/remindor-qt-windows.ico')] }]
)