# -*- coding: utf-8 -*-

import sys
from PyQt4.QtGui import *
from ngq_manager_app import QtSingleApplication
from ngq_client_table import Table

print sys.argv

appGuid = 'F3FF80BA-BA05-4277-8063-82A6DB9245A3'
app = QtSingleApplication(appGuid, sys.argv)
if app.isRunning():
	if len(sys.argv) > 1:
		app.sendMessage(sys.argv[1])	
	sys.exit(0)

w = Table()
app.messageReceived.connect(w.processURI)

if len(sys.argv) > 1:
	w.processURI(sys.argv[1])

w.show()

sys.exit(app.exec_())