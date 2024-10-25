import os

import serial


def getAllPorts():
    path = "/dev/"
    files = os.listdir(path)
    ports = []
    for file in files:
        if "tnt" in file:
            try:
                port = serial.Serial(path + file, exclusive=True)
                ports.append("COM" + file[3])
                port.close()
            except:
                pass
    ports.reverse()
    return ports


def connectToPort(port: str):
    try:
        com = serial.Serial("/dev/tnt" + port[3], exclusive=True)
        return com
    except:
        return serial.Serial()


def sendByte(port: serial.Serial, byte: str):
    port.write(byte.encode())


def getByte(port: serial.Serial):
    str = b""
    try:
        while True:
            str += port.read()
            try:
                str.decode()
                break
            except:
                pass
        return str.decode()
    except:
        pass