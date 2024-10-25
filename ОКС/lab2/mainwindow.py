import sys

import serial
from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QComboBox, QMainWindow, QMessageBox

import ports
import reader

from ui_form import UiMainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.sendPort = serial.Serial()
        self.receivePort = serial.Serial()
        self.threadPool = QThreadPool()
        self.portReader = reader.Reader(self.receivePort)
        self.updatePorts()
        self.bytesSent = 0
        self.data = ""
        self.ui.receivePortCombo.currentTextChanged.connect(self.changeReceivePort)
        self.ui.sendPortCombo.currentTextChanged.connect(self.changeSendPort)
        self.ui.clearMessageButton.clicked.connect(self.clearInput)
        self.ui.clearConsoleButton.clicked.connect(self.clearOutput)
        self.ui.messageEntry.realTextEdited.connect(self.sendData)

    def writeStats(self):
        self.ui.statusText.setPlainText(f"Bytes sent = {self.bytesSent}\n")
        packet = ports.toPacket(self.data, self.sendPort.port)
        stuffedPacket = ports.bitStuffing(packet)
        stuffedBits = ports.getStuffedBits(stuffedPacket)
        text = ""
        i = 0
        for bit in stuffedBits:
            if bit == "0":
                if stuffedPacket[i] == "\n":
                    text += "\\n"
                else:
                    text += stuffedPacket[i]
            else:
                text += '<font color ="#FF0000">' + stuffedPacket[i] + "</font>"
            i += 1
        text += "\n"
        self.ui.statusText.append(text)

    def changeReceivePort(self, port: str):
        self.portReader.stop()
        self.threadPool.clear()
        self.receivePort.close()
        if ports.connectToPort(port).port == None:
            QMessageBox.warning(
                self, "Warning", "This port is busy. The list of ports has been updated"
            )
            wasBlocked = self.ui.receivePortCombo.blockSignals(True)
            self.ui.receivePortCombo.setCurrentIndex(-1)
            self.ui.receivePortCombo.blockSignals(wasBlocked)
            self.updatePorts()
            return
        self.receivePort = ports.connectToPort(port)
        self.receivePort.timeout = 0.1
        self.portReader = reader.Reader(self.receivePort)
        self.portReader.signal.packetRead.connect(self.writeText)
        self.threadPool.start(self.portReader)
        self.ui.statusText.append(
            f"Port {port} is open for reading. \nBaudrate = {self.receivePort.baudrate} \nBytesize = {self.receivePort.bytesize} \nParity = {self.receivePort.parity} \nStopbits = {self.receivePort.stopbits}\nTimeout = {self.receivePort.timeout}\n"
        )
        self.updatePorts()

    def changeSendPort(self, port: str):
        self.clearInput()
        self.sendPort.close()
        if ports.connectToPort(port).port == None:
            QMessageBox.warning(
                self, "Warning", "This port is busy. The list of ports has been updated"
            )
            wasBlocked = self.ui.sendPortCombo.blockSignals(True)
            self.ui.sendPortCombo.setCurrentIndex(-1)
            self.ui.sendPortCombo.blockSignals(wasBlocked)
            self.ui.messageEntry.setEnabled(False)
            self.ui.messageEntry.set_text("Choose port")
            self.updatePorts()
            return
        self.bytesSent = 0
        self.ui.messageEntry.setEnabled(True)
        self.sendPort = ports.connectToPort(port)
        self.sendPort.write_timeout = 0.1
        self.ui.statusText.append(
            f"Port {port} is open for writing. \nBaudrate = {self.sendPort.baudrate} \nBytesize = {self.sendPort.bytesize} \nParity = {self.sendPort.parity} \nStopbits = {self.sendPort.stopbits}\nTimeout =  {self.sendPort.timeout}\n"
        )
        self.updatePorts()

    def clearInput(self):
        wasBlocked = self.ui.messageEntry.blockSignals(True)
        self.ui.messageEntry.clear()
        self.ui.messageEntry.previousText = ""
        self.ui.messageEntry.blockSignals(wasBlocked)

    def clearOutput(self):
        wasBlocked = self.ui.messageReceived.blockSignals(True)
        self.ui.messageReceived.clear()
        self.ui.messageReceived.previousText = ""
        self.ui.messageReceived.blockSignals(wasBlocked)


    def sendData(self, str: str):
        self.data += str[-1:]
        if len(self.data) == 15:
            try:
                packet = ports.toPacket(data=self.data, port=self.sendPort.port)
                packet = ports.bitStuffing(packet)
                ports.sendPacket(self.sendPort, packet)
                self.bytesSent += len(ports.bitStuffing(ports.toPacket(self.data, self.sendPort.port)).encode())
                self.writeStats()
                self.data = ""
            except:
                self.ui.messageEntry.set_text(self.ui.messageEntry.toPlainText()[:-15])
                QMessageBox.warning(
                    self, "Warning", "This port has no receiver counterpart active"
                )

    def writeText(self, data: str):
        self.ui.messageReceived.insertPlainText(data)
        cursor = self.ui.messageReceived.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.messageReceived.setTextCursor(cursor)

    def setBoxList(self, comboBox: QComboBox, without: list):
        portList = ports.getAllPorts()
        text = comboBox.currentText()
        if text != "":
            portList.append(text)
        try:
            portList.remove(without[0])
        except:
            pass
        try:
            portList.remove(without[1])
        except:
            pass
        portList.sort()
        wasBlocked = comboBox.blockSignals(True)
        comboBox.clear()
        comboBox.addItems(portList)
        comboBox.setCurrentText(text)
        if text == "":
            comboBox.setCurrentIndex(-1)
        comboBox.blockSignals(wasBlocked)

    def updatePorts(self):
        textWrite = self.ui.sendPortCombo.currentText()
        textRead = self.ui.receivePortCombo.currentText()
        next = ""
        prev = ""
        if textWrite != "":
            next = textWrite[:-1] + str(int(textWrite[3]) + 1)
        if textRead != "":
            prev = textRead[:-1] + str(int(textRead[3]) - 1)
        self.setBoxList(
            self.ui.sendPortCombo,
            [self.ui.receivePortCombo.currentText(), prev],
        )
        self.setBoxList(
            self.ui.receivePortCombo,
            [self.ui.sendPortCombo.currentText(), next],
        )
        if textWrite == "":
            self.ui.messageEntry.setEnabled(False)
            self.ui.messageEntry.set_text("Choose port")

    def onExit(self):
        self.portReader.stop()
        self.threadPool.clear()
        self.receivePort.close()
        self.sendPort.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    app.aboutToQuit.connect(widget.onExit)
    widget.show()
    sys.exit(app.exec())