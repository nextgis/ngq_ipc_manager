# -*- coding: utf-8 -*-

#******************************************************************************
#
# QGIS Launcher
# ---------------------------------------------------------
# Extended identify tool. Supports displaying and modifying photos
#
# Copyright (C) 2015-2016 NextGIS (info@nextgis.org)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************

import os
import sys

from PyQt4 import QtCore
from PyQt4 import QtGui

from ngq_manager_app import QtSingleApplication
from ngq_manager_tray_icon import SystemTrayIcon
from ngq_manager_worker import NGQLauncherWorker

import logging

appGuid = 'F3FF80BA-BA05-4277-8063-82A6DB9245A2'

host = "0.0.0.0"
port = 9999

def is_frozen():
    return hasattr(sys, "frozen")

def module_path():
    if is_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

logFormatter = logging.Formatter("%(asctime)s:\t%(levelname)s:\t%(message)s", datefmt = '%m/%d/%Y %I:%M:%S %p')
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(os.path.join(module_path(), "ngq_manager.log"))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
# rootLogger.addHandler(consoleHandler)


def main():
    app = QtSingleApplication(appGuid, [])

    argString = " ". join(sys.argv[1:])
    argString = QtCore.QString(argString.replace('\\', '\\\\'))

    if app.isRunning():
        logging.debug('Run second instance with args: ' + argString)
        app.sendMessage(argString)
        sys.exit(app.exit(0))

    logging.debug('Run with args: ' + argString)
    logging.debug('PID: %d' % QtGui.QApplication.applicationPid())

    trayicon = SystemTrayIcon(
        os.path.join(module_path(), "ngq.ico"),
    )
    trayicon.show()

    worker = NGQLauncherWorker(host, port, argString, trayicon)
    app.messageReceived.connect(worker.executeArgs)
    worker.ngqListChanged.connect(trayicon.showNGQs)
    worker.messageEmited.connect(trayicon.showMessage)
    worker.start()
    
    trayicon.showNGQ.connect(worker.showNGQ)
    trayicon.rereadConfig.connect(worker.reconfigure)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()