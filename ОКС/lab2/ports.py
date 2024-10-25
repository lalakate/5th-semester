import os

import serial

N = 15
FLAG = "10001111"
FLAG_LEN = len(FLAG)
SEARCH_BITS = "1000111"
ADD_BIT = "0"
SEARCH_LEN = len(SEARCH_BITS)

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


def sendPacket(port: serial.Serial, packet: str):
    port.write(packet.encode())
    
def getPacket(port: serial.Serial):
    try:
        return port.read_all().decode()
    except:
        return None

def toPacket(data: str, port: str):
    destinationAddress = "0000"
    FCS = "0"
    srcAddress = bin(int(port[-1:]))[2:]
    while len(srcAddress) < 4:
        srcAddress = "0" + srcAddress
    return FLAG + destinationAddress + srcAddress + data + FCS

def fromPacket(packet: str):
    return packet[16:-1]

def bitStuffing(packet):
    left = ""
    stuffedPacket = packet[:8]
    for bit in packet[8:]:
        left += bit
        if left == SEARCH_BITS:
            left += ADD_BIT
            stuffedPacket += left
            left = ""
        if len(left) == SEARCH_LEN:
            stuffedPacket += left[0]
            left = left[1:]
    if left != "":
        stuffedPacket += left
    return stuffedPacket

def deBitStuffing(packet):
    left = ""
    destuffedPacket = packet[:8]
    for bit in packet[8:]:
        left += bit
        if left[:-1] == SEARCH_BITS:
            destuffedPacket += left[:-1]
            left = ""
        if len(left) == SEARCH_LEN + 1:
            destuffedPacket += left[0]
            left = left[1:]
    if left != "":
        destuffedPacket += left
    return destuffedPacket 

def getStuffedBits(packet):
    left = ""
    stuffedBits = "0" * 8
    for bit in packet[8:]:
        left += bit
        if left[:-1] == SEARCH_BITS:
            stuffedBits += "0" * SEARCH_LEN + "1"
            left = ""
        if len(left) == SEARCH_LEN + 1:
            stuffedBits += "0"
            left = left[1:]
    if left != "":
        stuffedBits += "0" * len(left)
    return stuffedBits