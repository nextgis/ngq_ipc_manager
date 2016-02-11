import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Table(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        self.setWindowTitle("Emulator")

        data = [
            "1683BCAF15580D67E050007F01006372",
            "1FC731256324B5B5E050007F0100164A",
            "1FC73125631FB5B5E050007F0100164A",
            "1FC731256320B5B5E050007F0100164A",
            "1FC731256314B5B5E050007F0100164A",
            "1FC731256315B5B5E050007F0100164A",
            "1FB5993011EF778CE050007F0100090C",
            "1FB5993011F0778CE050007F0100090C",
            "1FB5993011F7778CE050007F0100090C",
            "1FB5993011F8778CE050007F0100090C",
            "1FB5993011F9778CE050007F0100090C",
            "1FB5993011FA778CE050007F0100090C",
            "1FC731256322B5B5E050007F0100164A",
            "1FC731256321B5B5E050007F0100164A",
            "1FB5993011E5778CE050007F0100090C",
            "1FB5993011E6778CE050007F0100090C",
            "1FD98F0ED90391A8E050007F010024B5",
            "1FC73125631DB5B5E050007F0100164A",
            "1FC73125631CB5B5E050007F0100164A",
            "1FB5993011E7778CE050007F0100090C",
            "1FB5993011E8778CE050007F0100090C",
            "1FC731256316B5B5E050007F0100164A",
            "1FC731256317B5B5E050007F0100164A",
            "1FC731256325B5B5E050007F0100164A",
            "1FC731256323B5B5E050007F0100164A",
            "1FC73125631AB5B5E050007F0100164A",
            "1FC73125631BB5B5E050007F0100164A",
            "1FB5993011E3778CE050007F0100090C",
            "1FB5993011E4778CE050007F0100090C",
            "1FB5993011E9778CE050007F0100090C",
            "1FB5993011EA778CE050007F0100090C",
            "1FB5993011EB778CE050007F0100090C",
            "1FB5993011EC778CE050007F0100090C",
            "1FB5993011ED778CE050007F0100090C",
            "1FB5993011EE778CE050007F0100090C",
            "1FB5993011F3778CE050007F0100090C",
            "1FB5993011F4778CE050007F0100090C",
            "1FB5993011FF778CE050007F0100090C",
            "1FB599301200778CE050007F0100090C",
            "1FB599301201778CE050007F0100090C",
            "1FB599301202778CE050007F0100090C",
            "1FB5993011F1778CE050007F0100090C",
            "1FB5993011F2778CE050007F0100090C",
            "1FB5993011FB778CE050007F0100090C",
            "1FB5993011FC778CE050007F0100090C",
            "1FB5993011FD778CE050007F0100090C",
            "1FB5993011FE778CE050007F0100090C",
            "1FB5993011F5778CE050007F0100090C",
            "1FB5993011F6778CE050007F0100090C",
            "1FB599301203778CE050007F0100090C",
            "1FB599301204778CE050007F0100090C",
            "1FC731256312B5B5E050007F0100164A",
            "1FC731256313B5B5E050007F0100164A",
            "1FC731256318B5B5E050007F0100164A",
            "1FC731256319B5B5E050007F0100164A",
            "1FC73125631EB5B5E050007F0100164A",
        ]

        self.__layout = QVBoxLayout(self)

        self.__list = QListWidget(self)
        self.__list.setMinimumSize(350, 250)
        self.__layout.addWidget(self.__list)


        for guidIndex in range(0, len(data)):
            item = QListWidgetItem("%d: %s" % (guidIndex, data[guidIndex]))
            item.setData(Qt.UserRole, data[guidIndex])
            self.__list.addItem(item)

        self.__list.itemDoubleClicked.connect(self.callMap)

    def callMap(self, item):
        menu = QMenu()
        ov_map = QAction("Overview map", menu)
        tech_sceme = QAction("Technological scheme", menu)
        mnem_diag = QAction("Mnemonic diagram", menu)
        menu.addAction(ov_map)
        menu.addAction(tech_sceme)
        menu.addAction(mnem_diag)
        action = menu.exec_(QCursor.pos())

        guid = item.data(Qt.UserRole).toString()
        uri = "ngq:position?guid=%s" % guid

        if action == ov_map:
            uri += "&project_type=overview_map"
        elif action == tech_sceme:
            uri += "&project_type=technological_scheme"
        elif action == mnem_diag:
            uri += "&project_type=mnemonic_diagram"
        print("uri: " + uri)
        
        QDesktopServices.openUrl(QUrl(uri))

    def processURI(self, uri):
        if type(uri) == QString:
            uri = unicode(uri.toUtf8())

        print("Process uri: " + uri)
        # visidata:showcard?id=96094?guid=1FC73125631CB5B5E050007F0100164A
        try:
            uri_parts = re.findall('(.+):(\w+)\?(.+)', uri)[0]
            command = uri_parts[1]
            args_str = uri_parts[2]

            print "    command: ", command
            args = {}
            for arg_str in args_str.split('?'):
                key_value = arg_str.split('=')
                args.update({key_value[0]: key_value[1]})
            
            print "    args: ", args

            if command == "showcard" and args.get("id", -1) == "96094":
                self.showCard(args.get("guid",""))

            if command == "showcard" and args.get("id", -1) == -1:
                self.showBalanceDoc(args.get("guid",""))

        except Exception as err:
            print "Bad command defenition: %s" % uri
            print "Err: %s" % str(err)

    def showCard(self, targetguid):
        self.showMinimized()
        self.showMaximized()

        print("Select guid: " + targetguid)
        for itemIndex in range(0, self.__list.count()):
            item = self.__list.item(itemIndex)
            guid = item.data(Qt.UserRole).toString()
            if guid == targetguid:
                self.__list.setCurrentRow(itemIndex)
                QMessageBox.information(
                    self,
                    "Card for GUID: %s" % guid,
                    "This is card for object with GUID: %s" % guid
                )
                return

        QMessageBox.critical(self, "Guid not found!", "Guid not found!")

    def showBalanceDoc(self, targetguid):
        self.showMinimized()
        self.showMaximized()

        print("Select guid: " + targetguid)
        for itemIndex in range(0, self.__list.count()):
            item = self.__list.item(itemIndex)
            guid = item.data(Qt.UserRole).toString()
            if guid == targetguid:
                self.__list.setCurrentRow(itemIndex)
                QMessageBox.information(
                    self,
                    "Balance for GUID: %s" % guid,
                    "This is balanced document for object with GUID: %s" % guid
                )
                return

        QMessageBox.critical(self, "Guid not found!", "Guid not found!")