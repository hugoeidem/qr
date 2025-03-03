from typing import TYPE_CHECKING
from constants import LEVEL_SAFTY_RANK, RS_BLOCK_TABLE, \
    CHARACTER_COUNT_LENGTH, ECI_codes, ALPHANUMERIC_TABLE
from functions import *
from galois_rs import rsBytes

if TYPE_CHECKING:
    from basic_reader import Basic_reader

def ECI_decoder(br: "Basic_reader"):
    
    # 8-24 following bits are the ECI identifier
    if not br.readBit():        # beginning is 0 means id is 8 bits
        id = br.readBits(7)
    elif not br.readBit():      # beginning is 10 means id is 16 bits
        id = br.readBits(14)
    else:                       # beginning is 11 means id is 24 bits
        id = br.readBits(21)

    # TODO error handling av id vars code_page inte finns i constants
    br.codepage = ECI_codes[id] # example codepage, id 26 = 'utf-8'

    if br.show_info:
        print("CODEPAGE ID:", id)
        print("CHANGING CODE PAGE TO:", ECI_codes[id])


def byte_decoder(br: "Basic_reader"):

    char_count_ind_length = CHARACTER_COUNT_LENGTH[0b0100][br.version]
    char_count = br.readBits(char_count_ind_length)

    # print(char_count)
    byte_list = br.readBytes(char_count)
    byte_seq = bytes(byte_list)

    try:
        return byte_seq.decode(br.codepage)
    except:
        print(f"Codepage {br.codepage} failed.")
        for codepage in ["latin-1", "utf-16be"]:
            print(f"Trying {codepage}...")
            try:
                return byte_seq.decode(codepage)
            except:
                print("it failed!")
    

def alphanumeric_decoder(br: "Basic_reader"):

    char_count_ind_length = CHARACTER_COUNT_LENGTH[0b0010][br.version]
    char_count = br.readBits(char_count_ind_length)

    pairs = char_count//2
    isOdd = char_count%2 == 1

    msg = ""

    for _ in range(pairs):
        bits = br.readBits(11)
        msg += ALPHANUMERIC_TABLE[bits//45]
        msg += ALPHANUMERIC_TABLE[bits%45]

    if isOdd:
        bits = br.readBits(6)
        msg += ALPHANUMERIC_TABLE[bits]

    return msg


def numeric_decoder(br: "Basic_reader"):
    
    char_count_ind_length = CHARACTER_COUNT_LENGTH[0b0001][br.version]
    char_count = br.readBits(char_count_ind_length)
    
    if br.show_info:
        print(f"NUMERIC: reading {char_count} chars of (10 bits each), = {char_count*10/8} bytes")

    msg = ""

    while char_count >= 3:
        bits = br.readBits(10)
        msg += str(bits)
        char_count -= 3

    if char_count == 2:
        msg += str(br.readBits(7))

    elif char_count == 1:
        msg += str(br.readBits(4))

    return msg


def checkForCorruption(br: "Basic_reader"):

    format = br.getUncookedFormat()
    level = binaryFromBitlist(format[0:2])
    level_rank = LEVEL_SAFTY_RANK[level]

    if br.show_info:
        print("level_rank:", level_rank)

    #  group 1                   group 2
    # (blocks, bytes, databytes, blocks, bytes, databtyes)
    block_info = RS_BLOCK_TABLE[br.version*4 + level_rank]

    if br.show_info:
        print("block_info:", block_info)

    if 3 == len(block_info):
        block_info = block_info + (0, 0, 0)

    block_count = block_info[0] + block_info[3]
    dblocks = [[] for _ in range(block_count)]
    eblocks = [[] for _ in range(block_count)]
    dcounts = [block_info[2] for _ in range(block_info[0])] + [block_info[5] for _ in range(block_info[3])]
    ecounts = [block_info[1]-block_info[2] for _ in range(block_info[0])] + \
              [block_info[4]-block_info[5] for _ in range(block_info[3])]

    i = 0
    indices = list(range(block_count))
    for _ in range(sum(dcounts)):
        index = indices[i%len(indices)]
        dblocks[index].append(br.readByte())
        dcounts[index] -= 1
        if dcounts[index] == 0: indices.remove(index)
        i += 1

    i = 0
    indices = list(range(block_count))
    for _ in range(sum(ecounts)):
        index = indices[i%len(indices)]
        eblocks[index].append(br.readByte())
        ecounts[index] -= 1
        if ecounts[index] == 0: indices.remove(index)
        i += 1

    br.resetPos()
    isValid = True

    for i in range(block_count):
        ecc = block_info[1] - block_info[2] if i < block_info[0] else block_info[4] - block_info[5]

        if rsBytes(dblocks[i], ecc) != eblocks[i]:
            isValid = False

    # Reverse block-interleaving and reorder the bitstream
    data = []

    for block in dblocks + eblocks:
        for byte in block:
            data += bitlistFromBinary(byte, 8)

    br.data = data
    return isValid




def kanji_decoder(br: "Basic_reader"):

    char_count_ind_length = CHARACTER_COUNT_LENGTH[0b1000][br.version]
    char_count = br.readBits(char_count_ind_length)
    
    byte_list = []

    for _ in range(char_count):
        i = br.readBits(13)
        a = i // 0xC0
        b = i % 0xC0
        reduced = (a << 8) + b

        if reduced <= 0x1ebc:
            reduced += 0x8140
        else:
            reduced += 0xC140

        byte_list.append(reduced >> 8) # extract high byte
        byte_list.append(reduced & 0xFF) # extract low byte

    msg = bytes(byte_list).decode("shift_jis")

    return msg
        
    
def fake_kanji_encoder(msg: str):

    out = []

    for c in msg:
        i  = int.from_bytes(c.encode("shift_jis"), "big")

        if 0x8140 <= i <= 0x9FFC:
            i -= 0x8140
            b = i & 0xFF
            a = i >> 8
            res = a * 0xC0 + b
            out.append(res)

        elif 0xE040 <= i <= 0xEBBF:
            i -= 0xC140
            b = i & 0xFF
            a = i >> 8
            res = a * 0xC0 + b
            out.append(res)

    return out
            