from header import *

# CHANGE TO APPROPRIATE DRIVE OF YOUR DEVICE!!!
drive = "\\\\.\\D:"

# read Boot sector of a specific drive
def read_bootSector(drive):
    bootSector = readSector(drive, 0)
    bytesPerSector = 512
    FAT_type = bootSector[0x52 : 0x52+8] # from offset 0x52 read 8 bytes
    Sc = bootSector[0xD]
    Sb = hex2dec(getHex(hex((bootSector[0xF]))) + getHex(hex(bootSector[0xE]))) # from offset 0xE read 2 bytes
    Sf = hex2dec(getHex(hex((bootSector[0x27]))) + getHex(hex(bootSector[0x26]))
                 + getHex(hex((bootSector[0x25]))) + getHex(hex(bootSector[0x24]))) # from offset 0x24 read 4 bytes
    Nf = bootSector[0x10] # read offset 0x10
    firstClusterRDET = hex2dec(getHex(hex((bootSector[0x2F]))) + getHex(hex(bootSector[0x2E]))
                               + getHex(hex((bootSector[0x2D]))) + getHex(hex(bootSector[0x2C]))) # from offset 0x2D read 3 bytes
    print("FAT Type: ", FAT_type, "\n") 
    print("Bytes Per Sector: ", bytesPerSector, '\n')
    print("Sectors Per Cluster: ", Sc, '\n')
    print("Number Of Sectors Before FAT Table: ", Sb, '\n')
    print("Sectors Per FAT Table: ", Sf, '\n')
    print("First Cluster Of RDET: ", firstClusterRDET, '\n')
    print("Number Of FAT Tables: ", Nf, '\n')
    print("----------------------------------------------------\n\n")
    readRDET(drive, Sc, Sb, Sf, Nf, firstClusterRDET, bytesPerSector)

info = [] # array to store informations of a file/directory in the drive

# read RDET of the drive
def readRDET(drive, Sc, Sb, Sf, Nf, firstClusterRDET, bytesPerSector):
    name = "" 
    cluster = firstClusterRDET
    startSec = (cluster - 2) * Sc + Sb + Sf * Nf
    for i in range(Sc):
        sector = readSector(drive, startSec + i) # iterate and read through every sectors in 1 cluster
        # 16 entries per sector
        for t in range(16):
            entryArr = []
            # An entry has size of 32 bytes
            for k in range(32):
                # entryArr is an array of integers values
                entryArr.append(sector[32 * t + k])
            if(entryArr[0] == 0xE5 or entryArr[0] == 0x00): 
                continue
            if(entryArr[0xB] != 0x0F):
                attribute = ""
                if(entryArr[0xB] == 32): 
                    attribute = "Archive"
                elif (entryArr[0xB] == 16):
                    attribute = "Directory"
                elif (entryArr[0xB] == 8):
                    attribute = "Vollabel"
                elif (entryArr[0xB] == 4): 
                    attribute = "System"
                elif(entryArr[0xB] == 32): 
                    attribute = "Hidden"
                else:   
                    attribute = "ReadOnly"               
                size = hex2dec(littleEndian(entryArr[0x1C : 0x1C + 4])) # from offset 0x1C read 4 bytes
                startCluster = hex2dec(littleEndian(entryArr[0x14 : 0x14 + 2])) + hex2dec(littleEndian(entryArr[0x1A : 0x1A + 2])) # from offset 0x14 read 2 bytes, from offset 0x1A read 2 bytes
                expansion = hex2string(entryArr[8 : 11]) # from offset 0x08 read 3 bytes
                if(name == ""):
                    name = hex2string(entryArr[0 : 8]) # from offset 0x00 read 8 bytes
                    if(expansion != "   "): 
                        name = name.strip()
                        name += '.' + expansion                
                name = name.strip()
                item = (name, attribute, size, startCluster, expansion)
                info.append(item)
                name = ""
            else:
                name = hex2string(entryArr[1 : 1 + 0xA]) + hex2string(entryArr[0xE : 0xE + 0xC]) + hex2string(entryArr[0x1C : 0x1C + 4]) + name # read file/directory name from subentries
    
    # display info of the current drive
    for i in range(len(info)):
        print("Name: ", info[i][0], ", Attribute: ", info[i][1], ", Size: ", info[i][2], ", Starting Cluster: ", info[i][3])
        print('\n')

    # Access file/directory of the current drive
    while(True):
        readSDET(drive, Sc, Sb, Sf, Nf, firstClusterRDET, bytesPerSector)
        answer = input("Input 0 to exit, 1 to continue: ")
        print('\n')
        if(answer == 0): return

def printContent(drive, startCluster, size, Sc, Sb, Sf, Nf, bytesPerSector):
    clusterSize = 512 * Sc
    currentCluster = startCluster
    remainingBytes = size
    content = ""
    
    while remainingBytes > 0:
        sector = readSector(drive, (currentCluster - 2) * Sc + Sb + Sf * Nf)
        bytesToRead = min(remainingBytes, clusterSize)
        content += bytes(sector[:bytesToRead]).decode("utf-8", errors="ignore")
        remainingBytes -= bytesToRead
        fatOffset = currentCluster + (currentCluster // 2)
        fatSector = readSector(drive, Sb + fatOffset // bytesPerSector)
        if currentCluster % 2 == 0:
            currentCluster = int.from_bytes(fatSector[(fatOffset % bytesPerSector):(fatOffset % bytesPerSector) + 2], byteorder='little') & 0xFFF
        else:
            currentCluster = int.from_bytes(fatSector[(fatOffset % bytesPerSector) - 1:(fatOffset % bytesPerSector) + 1], byteorder='little') >> 4
        if currentCluster >= 0xFF8:
            break
    
    print(content)

def readSDET(drive, Sc, Sb, Sf, Nf, firstClusterRDET, bytesPerSector):
    name = input("File/Directory To Open: ")
    index = -1
    for i in range(len(info)):
        if (info[i][0].lower() == name.lower()):
            index = i
            break
    if (index == -1):
        print("File/Directory Doesn't Exist!!!")
    elif info[index][1] == "Archive" and info[index][4].lower() == "txt":
        startCluster = info[index][3]
        size = info[index][2]
        printContent(drive, startCluster, size, Sc, Sb, Sf, Nf, bytesPerSector)
    elif(info[index][1] == "Directory"):
        readRDET(drive, Sc, Sb, Sf, Nf, info[index][3], bytesPerSector)
    else:
        print("Please Use Approriate App To Open.")
        return
    
    print('\n')

read_bootSector(drive)
