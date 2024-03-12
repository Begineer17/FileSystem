from header import *

def get_attribute_type(val):
    if val == 16: return "$STANDARD_INFORMATION"
    elif val == 32: return "$ATTRIBUTE_LIST"
    elif val == 48: return "$FILE_NAME"
    elif val == 64: return "$OBJECT_ID"
    elif val == 80: return "$SECURITY_DESCRIPTOR"
    elif val == 96: return "$VOLUME_NAME"
    elif val == 112: return "$VOLUME_INFORMATION"
    elif val == 128: return "$DATA"
    elif val == 144: return "$INDEX_ROOT"
    elif val == 160: return "$INDEX_ALLOCATION"
    elif val == 176: return "$BITMAP"
    elif val == 192: return "$REPARSE_POINT"
    elif val == 208: return "$EA_INFORMATION"
    elif val == 224: return "$EA"
    elif val == 256: return "$LOGGED_UTILITY_STREAM"

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

    readMFT(drive, startClusterMFT, Sc)

info = []

def readMFT(drive, startClusterMFT, Sc):
    startSec = startClusterMFT * Sc
    for i in range(0, Sc, 2):
        entry = readSector(drive, startSec + i) + readSector(drive, startSec + i + 1)
        signal = []
        for t in range(4):
            signal.append(entry[t])
        if hex2string(signal) == "BAAD":
            continue
        flag = hex2dec(littleEndian2(entry, 0x16, 0x17))
        if flag != 1 and flag != 2:
            continue
        isDirectory = False
        if(flag == 2):
            isDirectory = True
        attributeOffset = hex2dec(littleEndian2(entry, 0x14, 0x15))
        while hex2dec(littleEndian2(entry, attributeOffset, attributeOffset + 7) != 0xFFFFFFFF):
            attributeSize = hex2dec(littleEndian2(entry, attributeOffset + 4, attributeOffset + 7))
            contentSize =  hex2dec(littleEndian2(entry, attributeOffset + 16, attributeOffset + 19))
            startContent = attributeOffset + hex2dec(littleEndian2(entry, attributeOffset + 20, attributeOffset + 21))
            attributeType = []
            attr = None
            name = ""
            for t in range(3):
                attributeType.append(entry[attributeOffset + i])
            if get_attribute_type(hex2dec(attributeType)) == "$STANDARD_INFORMATION":
                attr = getAttributeOfStandard(hex2dec(littleEndian2(entry, startContent + 32, startContent + 35)))
            elif get_attribute_type(hex2dec(attributeType)) == "$FILE_NAME":
                nameLen = entry[startContent + 64]
                nameArr = []
                for t in range(nameLen):
                    nameArr.append(entry[66 + t])
                name = hex2string(nameArr)
            attributeOffset += attributeSize
        info.append((isDirectory, attr, name))
    for i in range(len(info)):
        print("Name: ", info[i][2])
        print("Attribute: ", info[i][1], ", Directory" if info[i][0] == True else "")

readSector("\\\\.\\E:", 0)
    

