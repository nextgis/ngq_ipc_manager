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
import re
import sys
import json
import shlex
import locale
import logging
import argparse
import subprocess

from functools import partial

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtNetwork

def is_frozen():
    return hasattr(sys, "frozen")

def module_path():
    if is_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

def samefile(path1, path2):
    #return os.stat(path1) == os.stat(path2)
    return os.path.normcase(os.path.normpath(path1)) == \
           os.path.normcase(os.path.normpath(path2))
    
class NGQLauncherWorker(QtCore.QObject):
    ngqListChanged = QtCore.pyqtSignal(list)
    messageEmited = QtCore.pyqtSignal(unicode, unicode, int, int)
    
    startExecuteArgs = QtCore.pyqtSignal(unicode)

    def __init__(self, host, port, argString, parent=None):
        super(NGQLauncherWorker, self).__init__(parent)
        
        self.__host = host
        self.__port = port
        self.__argString = argString
        self.__initializationTime = 2
        
        self.__ngqConnections = {}
        self.__waitingTasks = {}

        self.__waitForStartQGIS = 10
        self.__qgisBat = unicode(os.path.join(module_path(), "..", "bin","qgis.bat"))
        self.__configuration = {}
    
    def start(self):
        self.messageEmited.emit(
            "NGQ Manager",
            "Initialization" + "...",
            QtGui.QSystemTrayIcon.Information,
            100
        )
        self.tcpServer = QtNetwork.QTcpServer()
        self.tcpServer.listen(QtNetwork.QHostAddress(self.__host), self.__port)
        self.tcpServer.newConnection.connect(self.__newConnectionHandle)

        self.configure()

        self.ngqListChanged.connect(self.__chooseWaitingTasksForProject)
        self.__putToWaitingTasks(partial(self.executeArgs, self.__argString), None, self.__initializationTime)
    
    def reconfigure(self):
        res = self.configure()
        if res is True:
            self.messageEmited.emit(
                "NGQ Manager",
                "Configuration success",
                QtGui.QSystemTrayIcon.Information,
                100
            )
    def configure(self):
        self.__configuration = {}
        try:
            with open(os.path.join(module_path(), "project_types.json")) as project_types_file:
                project_types_struct = json.load(
                    project_types_file
                )
                for project_type, project_type_config in project_types_struct.items():

                    if project_type_config.has_key("project"):
                        self.__configuration[project_type] = project_type_config["project"]
                        continue

                    if project_type_config.has_key("config"):
                        with open(os.path.join(module_path(), project_type_config["config"])) as project_type_file:
                            self.__configuration[project_type] = json.load(project_type_file)
            return True
        except Exception as err:
            msg = "Cann't parse configuration file: " + str(err)
            logging.error(msg)
            self.messageEmited.emit(
                "NGQ Manager",
                msg + "\n See logs!",
                QtGui.QSystemTrayIcon.Critical,
                1000
            )
            return False

    def __getProjectByProjectType(self, projectType, addition_parameter):
        projInfo = self.__configuration.get(projectType)
        if isinstance(projInfo, dict):
            for key, value in addition_parameter.items():
                d = projInfo.get(key, {})
                project_index = d.get(value)

                if project_index is None:
                    continue
                try:
                    projects = projInfo.get("projects", [])
                    return projects[project_index]
                except IndexError:
                    continue
            return None
        else:
            return projInfo

    def __parseArgs(self, argString):
        argString = unicode(argString.toUtf8())
        parser = argparse.ArgumentParser()
        parser.add_argument("--uri", help="call uri")
        parser.add_argument("--qgis", help="bat for run qgis")
        parser.add_argument("--qgis_project", help="qgis project file")
        args = parser.parse_args(shlex.split(argString))
        
        return args

    def executeArgs(self, argString, by_timer=False):
        logging.debug("Execute with args: " + argString)

        args = self.__parseArgs(argString)
        if args.qgis is not None:
            self.__qgisBat = args.qgis

        if args.uri is not None:
            # ngq:position?guid=1FC731256324B5B5E050007F0100164A&project_type=[overview_map|technological_scheme|mnemonic_diagram]
            command = None
            command_args = {}
            try:
                uri_parts = re.findall('(.+):(.+)\?(.+)', args.uri)[0]
                command = uri_parts[1]
                args_str = uri_parts[2]

                for arg_str in args_str.split('&'):
                    key_value = arg_str.split('=')
                    command_args.update({key_value[0]: key_value[1]})
            except Exception:
                logging.error("Cann't parse uri: " + unicode(args.uri))
                return

            if command == "position":
                self.__sendPositionCommand(command_args)
            else:
                logging.error("Unknown command: " + unicode(command))
                return

    def __newConnectionHandle(self):
        clientConnection = self.tcpServer.nextPendingConnection()
        self.__ngqConnections[clientConnection] = {}
        logging.debug("New connection established self.__ngqConnections: " + str(self.__ngqConnections))

        clientConnection.disconnected.connect(self.__removeConnection)
        clientConnection.readyRead.connect(self.__readFromClient)

    def __removeConnection(self):
        clientConnection = self.sender()
        self.__ngqConnections.pop(clientConnection)
        logging.debug("Connection lost self.__ngqConnections: " + str(self.__ngqConnections))
        self.ngqListChanged.emit(self.__ngqConnections.items())

    def __readFromClient(self):
        clientConnection = self.sender()
        data = unicode(clientConnection.readAll())
        for line in data.split('\n')[:-1]:
            try:
                struct = json.loads(unicode(line))

                if struct.has_key("qgis_state"):
                    self.__ngqConnections[clientConnection].update(struct["qgis_state"])
                    logging.debug("Client change status self.__ngqConnections: " + str(self.__ngqConnections))
                    self.ngqListChanged.emit(self.__ngqConnections.items())

                if struct.has_key("command"):
                    commandStruct = struct["command"]
                    logging.debug("Receive command: " + str(commandStruct))
                    if commandStruct.get("name") == "send_uri":
                        self.__callURI(commandStruct.get("args",""))
            except:
                logging.error("Cann't parse line: " + unicode(line))

    def __sendToClient(self, clientConnection, data):
        dataString = ""
        try:
            dataString = json.dumps(data)
        except Exception:
            logging.error("Cann't parse data: " + unicode(data))
            return

        message = QtCore.QByteArray(dataString)
        clientConnection.write(message + '\n')

    def __putToWaitingTasks(self, function, ngq_project, timeout):
        timerId = self.startTimer(timeout * 1000)
        self.__waitingTasks[function] = [timerId, ngq_project] 

    def timerEvent(self, event):
        timerId = event.timerId()
        self.killTimer(timerId)
        for function, conditions in self.__waitingTasks.items():
            if conditions[0] == timerId:
                function()
                self.__waitingTasks.pop(function)
                break

    def __chooseWaitingTasksForProject(self, ngqList):
        projects = [ ngq[1].get("open_project","") for ngq in ngqList]
        for function, conditions in self.__waitingTasks.items():
            targetProject = conditions[1]
            if targetProject is None:
                continue

            for proj in projects:
                print "conditions[1]: ", conditions[1]
                print "proj: ", proj
                if samefile(conditions[1], proj):
                    function()
                    self.__waitingTasks.pop(function)
                    break

    def showNGQ(self, ngqConnection):
        commandDesc = {
            "command":{
                "name": "activate",
                "args": {}
            }
        }
        self.__sendToClient(ngqConnection, commandDesc)

    def __sendPositionCommand(self, args, by_timer=False):
        logging.debug("Send position command. self.__ngqConnections: " + str(self.__ngqConnections))

        if args.has_key("project_type") == False:
            self.messageEmited.emit(
                "NGQ Manager",
                "Project not found! See logs\n",
                QtGui.QSystemTrayIcon.Critical,
                1000
            )
            logging.error("Send position command. ERROR: No project_type attribute in args " + str(args))
            return
        project_type = args.get("project_type")

        projectFilename = self.__getProjectByProjectType(project_type, args)
        
        if projectFilename is None:
            self.messageEmited.emit(
                "NGQ Manager",
                "Project not found! See logs\n",
                QtGui.QSystemTrayIcon.Critical,
                1000
            )
            logging.error("Send position command. ERROR: No project for args " + str(args))
            return

        logging.debug("Send position comman. Need projectFilename: " + projectFilename)

        ngqConnection = None
        for __ngqConnection, attrs in self.__ngqConnections.items():
            if samefile(attrs.get("open_project"), projectFilename):
                logging.debug("Send position comman. Found: " + attrs.get("open_project"))
                ngqConnection = __ngqConnection
                break

        if ngqConnection is not None:
            args.pop("project_type")

            commandDesc = {
                "command":{
                    "name": "position",
                    "args": args
                }
            }
            self.__sendToClient(ngqConnection, commandDesc)
        else:
            if by_timer == False:
                
                if not os.path.exists(projectFilename):
                    self.messageEmited.emit(
                        "NGQ Manager",
                        "Project file not exist! See logs\n",
                        QtGui.QSystemTrayIcon.Critical,
                        1000
                    )
                    logging.error("Send position command. Project file %s not exist" % str(projectFilename))
                    return
                    
                try:
                    cmd = [
                        self.__qgisBat.encode(locale.getpreferredencoding()),
                        u"--project".encode(locale.getpreferredencoding()),
                        projectFilename.encode(locale.getpreferredencoding())
                    ]
                    logging.error("Send position command. Try run command with args: %s" % (str(cmd), ))
                    # subprocess.check_call(cmd)
                    subprocess.Popen(cmd, close_fds=True)
                except Exception as err:
                    self.messageEmited.emit(
                        "NGQ Manager",
                        "Cann't run qgis! See logs\n",
                        QtGui.QSystemTrayIcon.Critical,
                        1000
                    )
                    logging.error("Send position command. Cann't run qgis with args: %s. Err: %s" % (str(cmd), str(err)))
                    return
                
                self.__putToWaitingTasks(
                    partial(self.__sendPositionCommand, args, True),
                    projectFilename,
                    self.__waitForStartQGIS
                )
                
            else:
                self.messageEmited.emit(
                    "NGQ Manager",
                    "Appropriate qgis not found!\n" + \
                    "Possible causes:\n" + \
                    "\t1. QGIS not run complite\n" + \
                    "\t2. QGIS IPC plugin not run\n",
                    QtGui.QSystemTrayIcon.Critical,
                    1000
                )

    def __callURI(self, uri):
        logging.debug("Call URI: " + str(uri))
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(uri))
