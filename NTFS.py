from header import *

def getAttributeOfStandard(flagVal):
    if (flagVal == 0x0001): return "Read Only"
    elif (flagVal == 0x0002): return "Hidden"
    elif (flagVal == 0x0004): return "System"
    elif (flagVal == 0x0020): return "Archive"
    elif (flagVal == 0x0040): return "Device"
    elif (flagVal == 0x0080): return "Normal"
    elif (flagVal == 0x0100): return "Temporary"
    elif (flagVal == 0x0200): return "Spares File"
    elif (flagVal == 0x0400): return "Reparse Point"
    elif (flagVal == 0x0800): return "Compressed"
    elif (flagVal == 0x1000): return "Offline"
    elif (flagVal == 0x2000): return "For Faster Searching Only"
    elif (flagVal == 0x4000): return "Encrypted"

def littleEndian2(arr, start, end):
    res = ""
    while (end != start):
        res += getHex(hex(arr[end]))
        end -= 1
    return res
    
def readVBR(drive):
    volumeBootRecord = readSector(drive, 0)
    Sc = volumeBootRecord[0x0D]
    diskSecs = hex2dec(littleEndian2(volumeBootRecord, 0x28, 0x28 + 8))
    startClusterMFT = hex2dec(littleEndian2(volumeBootRecord, 0x30, 0x30 + 8))
    entrySize = volumeBootRecord[0x40]

    print("File System: NTFS")
    print("Number Of Sectors Per Cluster: ", Sc, '\n')
    print("Number Of Sectors Of Disk: ", diskSecs, '\n')
    print("Beginning Cluster Of MFT: ", startClusterMFT, '\n')
    print("MFT Entry's Size: ", entrySize, "\n")

readSector("\\\\.\\E:", 0)
    

