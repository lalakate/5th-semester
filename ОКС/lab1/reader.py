import time

import serial
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

import ports


class ReaderSignal(QObject):
    byteRead = Signal(str)


class Reader(QRunnable):
    def __init__(self, port: serial.Serial, *args, **kwargs):
        super().__init__()
        self.port = port
        self.args = args
        self.kwargs = kwargs
        self.signal = ReaderSignal()
        self.running = True

    @Slot()
    def run(self):
        while self.running:
            byte = ports.getByte(self.port)
            self.signal.byteRead.emit(byte)
            time.sleep(0.01)

    def stop(self):
        self.running = False