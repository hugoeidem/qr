
from constants import ALIGNMENT_PATTERN_TABLE

def binaryFromBitlist(bitlist):
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out

def bitlistFromBinary(binary, length):
    return [(binary >> i) & 1 for i in range(length-1, -1, -1)]

def strFromBitlist(bitlist):
    return "".join(str(i) for i in bitlist)

def print2dArray(array):
    border = "██"
    print(border*(len(array[0]) + 2))
    for row in array:
        print(border + ''.join('██' if not x else '  ' for x in row) + border)
    print(border*(len(array[0]) + 2))

def gridprint(array, points=None):
    wall = ['//']+['0'+str(i) if i < 10 else str(i) for i in range(len(array[0]))]+['//']
    snake = ['@@', '&&', '[]', '//', '--', '..']

    size = len(array[0]) + 2
    print("".join(wall[:size]))
    for i, row in enumerate(array):
        print(wall[i+1], end="")
        for j, char in enumerate(row):
            x = '██' if not char else '  '

            if points and (i, j) in points:
                x = snake[points.index((i, j))]

            print(x, end="")
        print(wall[i+1])
    print("".join(wall[:size]))

if __name__=='__main__':
    import basic_reader

def zeros2d(size):
    return [[0 for _ in range(size)] for _ in range(size)]

def getValidPositions(ver: int): 
    """
    Version ver starts at 0!

    Returns 2d-array with valid positions represented by 1's.
    """
    
    size = 21 + ver*4
    out = [[1 for _ in range(size)] for _ in range(size)]

    # draw finder patterns, format bits and dark module
    drawZeros(out, 9, 9, 0, 0)
    drawZeros(out, 9, 8, size-8, 0)
    drawZeros(out, 8, 9, 0, size-8)

    alignments_positions = ALIGNMENT_PATTERN_TABLE[ver]

    # draw alignment patterns
    for row in alignments_positions:
        for col in alignments_positions:
            if out[row][col]:
                drawZeros(out, 5, 5, row-2, col-2)
            if out[col][row]:
                drawZeros(out, 5, 5, col-2, row-2)

    # draw timing patterns
    drawZeros(out, 1, size, 0, 6)
    drawZeros(out, size, 1, 6, 0)

    # draw informations areas
    if ver+1 >= 7:
        drawZeros(out, 3, 6, 0, size-8-3)
        drawZeros(out, 6, 3, size-8-3, 0)

    return out

def drawZeros(arr, width, height, row, col):
    for r in range(height):
        for c in range(width):
            arr[row+r][col+c] = 0

def drawOnes(arr, width, height, row, col):
    for r in range(height):
        for c in range(width):
            arr[row+r][col+c] = 1

def drawFinder(arr, row, col):
    drawOnes(arr, 7, 7, row, col)
    drawZeros(arr, 5, 5, row+1, col+1)
    drawOnes(arr, 3, 3, row+2, col+2)

def drawAlignment(arr, row, col):
    row -= 2
    col -= 2
    drawOnes(arr, 5, 5, row, col)
    drawZeros(arr, 3, 3, row+1, col+1)
    arr[row+2][col+2] = 1

def getPattern(ver: int):
    """
    Version ver starts at 1!

    Returns 2d-array of static pattern based on version.
    """

    size = 21 + 4*ver
    out = [[None for _ in range(size)] for _ in range(size)]
    drawFinder(out, 0, 0)
    drawFinder(out, 0, size-7)
    drawFinder(out, size-7, 0)

    return out

def confirmFormat(format: list[int]):
    info = binaryFromBitlist(format[0:5])
    parity = binaryFromBitlist(format[5:15])

    # x^10 + x^8 + x^5 + x^4 + x^2 + x + 1
    # observe binary representation is 11 digits
    generator = 0b10100110111

    # pad info bits to make 15-bit sequence
    info <<= 10

    # account for beginning zeros
    info_length = binLength(info)

    # reduce info until its the same length as the generator
    while info_length >= 11:
        info ^= generator << (info_length - 11) # XOR info with same length padded generator
        info_length = binLength(info) # get calculate new length

    # info should now have become equal to the input parity bits
    return info == parity

def binLength(binary: int):
    """
        Returns amount of bits in binary representation
    """
    out = 0
    while binary:
        binary >>= 1
        out += 1
    return out


if __name__=='__main__':

    confirmFormat([0,1,1,0,0])