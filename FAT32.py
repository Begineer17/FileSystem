import os

def readSector(drive, sectorNo):
    with open(drive, 'rb') as rS:
        rS.seek(sectorNo * 512)
        return rS.read(512)
    
def getHex(str):
    return str[2:].zfill(2)

def littleEndian(arr):
    arr = arr[::-1]
    res = ""
    for i in range(len(arr)):
        res += getHex(hex(arr[i]))
    return res

def hex2dec(hex_str):
    try:
        return int(hex_str, 16)
    except ValueError:
        print("Invalid hexadecimal input:", hex_str)
        return None 

def read_bootSector(drive):
    bootSector = readSector(drive, 0)
    bytesPerSector = 512
    FAT_type = bootSector[0x52 : 0x52+8]
    Sc = bootSector[0xD]
    Sb = hex2dec(getHex(hex((bootSector[0xF]))) + getHex(hex(bootSector[0xE])))
    Sf = hex2dec(getHex(hex((bootSector[0x27]))) + getHex(hex(bootSector[0x26])) + getHex(hex((bootSector[0x25]))) + getHex(hex(bootSector[0x24])))
    Nf = bootSector[0x10]
    firstClusterRDET = hex2dec(getHex(hex((bootSector[0x2F]))) + getHex(hex(bootSector[0x2E])) +getHex(hex((bootSector[0x2D]))) + getHex(hex(bootSector[0x2C])))
    print("FAT Type: ", FAT_type, "\n") 
    print("Bytes Per Sector: ", bytesPerSector, '\n')
    print("Sectors Per Cluster: ", Sc, '\n')
    print("Number Of Sectors Before Boot Sector: ", Sb, '\n')
    print("Sectors Per FAT Table: ", Sf, '\n')
    print("First Cluster Of RDET: ", firstClusterRDET, '\n')
    print("Number Of FAT Tables: ", Nf, '\n')
    print("----------------------------------------------------\n\n")
    readRDET(drive, Sc, Sb, Sf, Nf, firstClusterRDET)

def hex2string(str):
    res = ""
    for i in range(len(str)):
        if(str[i] == 0x00 or str[i] == 0xFF): 
            continue
        res += chr(str[i])
    return res

info = []
        
def readRDET(drive, Sc, Sb, Sf, Nf, firstClusterRDET):
    name = ""
    cluster = firstClusterRDET
    startSec = (cluster - 2) * Sc + Sb + Sf * Nf
    for i in range(Sc):
        sector = readSector(drive, startSec + i)
        for t in range(16):
            entryArr = []
            for k in range(32):
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
                
                size = hex2dec(littleEndian(entryArr[0xC : 0xC + 4]))
                startCluster = hex2dec(littleEndian(entryArr[0x14 : 0x14 + 2])) + hex2dec(littleEndian(entryArr[0x1A : 0x1A + 2]))
                expansion = hex2string(entryArr[8 : 11])
                if(name == ""):
                    name = hex2string(entryArr[0 : 8])
                    if(expansion != "   "): 
                        name = name.strip()
                        name += '.' + expansion                
                name = name.strip()
                item = (name, attribute, size, startCluster, expansion)
                info.append(item)
                name = ""
            else:
                name = hex2string(entryArr[1 : 1 + 0xA]) + hex2string(entryArr[0xE : 0xE + 0xC]) + hex2string(entryArr[0x1C : 0x1C + 4]) + name
    

    for i in range(len(info)):
        print("Name: ", info[i][0], ", Attribute: ", info[i][1], ", Size: ", info[i][2], ", Starting Cluster: ", info[i][3])
        print('\n')
        
    while(True):
        readSDET(drive, Sc, Sb, Sf, Nf, firstClusterRDET)
        answer = input("Input 0 to exit, 1 to continue: ")
        print('\n')
        if(answer == 0): return

def readSDET(drive, Sc, Sb, Sf, Nf, firstClusterRDET):
    name = input("File/Directory To Open: ")
    index = -1
    for i in range(len(info)):
        if (info[i][0].lower() == name.lower()):
            index = i
            break
    if (index == -1):
        print("File/Directory Doesn't Exist!!!")
    # elif(info[index][1] == "Archive" and info[index][4] == "TXT"):
    #     printContent()
    elif(info[index][1] == "Directory"):
        readRDET(drive, Sc, Sb, Sf, Nf, info[index][3])
    else:
        print("Please Use Approriate App To Open.")
        return
    
    print('\n')

read_bootSector("\\\\.\\D:")
