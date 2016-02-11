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

from functools import partial

from PyQt4 import QtGui
from PyQt4 import QtCore

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    showNGQ = QtCore.pyqtSignal(object)
    rereadConfig = QtCore.pyqtSignal()
    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, QtGui.QIcon(icon), parent)
        self.menu = QtGui.QMenu(parent)
        self.rereadConfigAction = self.menu.addAction("Reread config")
        self.rereadConfigAction.triggered.connect(self.rereadConfig.emit)
        self.exitAction = self.menu.addAction("Exit")
        self.exitAction.triggered.connect(QtGui.QApplication.instance().quit)
        self.setContextMenu(self.menu)

        self.__ngqActions = []

    def showNGQs(self, ngqs):
        for action in self.__ngqActions:
            self.menu.removeAction(action)

        self.__ngqActions = []

        for ngq_connection, ngq in ngqs:
            action = QtGui.QAction("%d: %s" % (ngq.get("pid", -1), ngq.get("open_project", "xxx")), self.menu)
            action.triggered.connect(partial(self.__showNGQ, ngq_connection))
            self.__ngqActions.append(action)
            self.menu.insertAction(self.rereadConfigAction, action)

        self.__ngqActions.append(self.menu.insertSeparator(self.rereadConfigAction))

    def __showNGQ(self, ngqConnection):
        self.showNGQ.emit(ngqConnection)