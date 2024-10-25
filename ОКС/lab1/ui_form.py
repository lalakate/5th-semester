from PySide6.QtCore import QMetaObject
from PySide6.QtWidgets import (QComboBox, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout)

from nodeletetextedit import NoDeleteTextEdit

class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("COM ports communication")
        MainWindow.setGeometry(100, 100, 400, 600)
        MainWindow.setStyleSheet("background-color: rgba(192, 217, 171, 255); color: black;")

        buttonStyle = "background-color: white; color: black;"
        comboStyle = "background-color: white; color: black;"

        self.sendPortCombo = QComboBox(MainWindow)
        self.sendPortCombo.setStyleSheet(comboStyle)
        self.receivePortCombo = QComboBox(MainWindow)
        self.receivePortCombo.setStyleSheet(comboStyle)

        self.messageEntry = NoDeleteTextEdit(MainWindow)
        self.messageEntry.setPlaceholderText("Type message...")
        self.messageEntry.setStyleSheet("background-color: white; color: black;")

        self.messageReceived = QTextEdit(MainWindow)
        self.messageReceived.setReadOnly(True)
        self.messageReceived.setPlaceholderText("Receiving messages...")
        self.messageReceived.setStyleSheet("background-color: white; color: black;")

        self.statusText = QTextEdit(MainWindow)
        self.statusText.setReadOnly(True)
        self.statusText.setPlaceholderText("Not started")
        self.statusText.setStyleSheet("background-color: white; color: black;")

        self.clearConsoleButton = QPushButton("Clear received messages", MainWindow)
        self.clearConsoleButton.setStyleSheet(buttonStyle)

        self.clearMessageButton = QPushButton("Clear message entry", MainWindow)
        self.clearMessageButton.setStyleSheet(buttonStyle)

        portLayout = QHBoxLayout()
        portLayout.addWidget(QLabel("Sender port:"))
        portLayout.addWidget(self.sendPortCombo)
        portLayout.addWidget(QLabel("Receiver port:"))
        portLayout.addWidget(self.receivePortCombo)

        messageLayout = QVBoxLayout()
        messageLayout.addWidget(QLabel("Message:"))
        messageLayout.addWidget(self.messageEntry)
        messageLayout.addWidget(self.clearMessageButton)

        receiveLayout = QVBoxLayout()
        receiveLayout.addWidget(QLabel("Received message:"))
        receiveLayout.addWidget(self.messageReceived)
        receiveLayout.addWidget(self.clearConsoleButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(portLayout)
        mainLayout.addLayout(messageLayout)
        mainLayout.addLayout(receiveLayout)
        mainLayout.addWidget(QLabel("Status:"))
        mainLayout.addWidget(self.statusText)

        centralWidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(centralWidget)
        centralWidget.setLayout(mainLayout)

        self.clearMessageButton.clicked.connect(self.messageEntry.clear)
        self.clearConsoleButton.clicked.connect(self.messageReceived.clear)

        QMetaObject.connectSlotsByName(MainWindow)

