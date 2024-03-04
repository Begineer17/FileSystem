def readSector(drive, sectorNo):
    with open(drive, 'rb') as rS:
        rS.seek(sectorNo * 512)
        return rS.read(512)
    
def getHex(str):
    return str[2:].zfill(2)

# arrr must be an array of integers 
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

# str must be an array of integers 
def hex2string(str):
    res = ""
    for i in range(len(str)):
        if(str[i] == 0x00 or str[i] == 0xFF): 
            continue
        res += chr(str[i])
    return res
