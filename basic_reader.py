

from PIL import Image
import numpy as np
from functions import *
from constants import MASKS
from decoder_functions import *
from base_qr_processor import BaseQRProcessor

class Basic_reader(BaseQRProcessor):
    def __init__(self, image_path, show_info = 0):
        self.show_info = show_info
        
        self.getGrid(image_path)
        self.isMasked = True

        size = len(self.grid)
        assert size % 2 != 0 and size >= 21
        self.version = (len(self.grid) - 21) // 4  # starts at 0, add 1 for "real" version
        if self.show_info:
            print("Version:", self.version+1)
        self.codepage = "utf-8"
        self.bytes_read = 0
        self.bits_read = 0
        self.data = None
        
        super().__init__(self.version, self.grid)

    def getGrid(self, image_path):
        """
            Turns a png into a 2d array like a qr-code
        """

        image = Image.open(image_path).convert("L")
        img = np.array(image)
        image.close()
        img = img < 128

        bsum = lambda arr : sum([int(i) for i in arr])

        r = c = 0
        r2, c2 = img.shape
        while bsum(img[r, :]) == 0: r += 1
        while bsum(img[r2-1, :]) == 0: r2 -= 1
        while bsum(img[:, c]) == 0: c += 1
        while bsum(img[:, c2-1]) == 0: c2 -= 1

        img = img[r:r2, c:c2]
        
        precision = 5 # 
        lines_checked = 3

        rows = []
        cols = []

        # get lines where there are big differences in pixels
        old = [bsum(img[i, :]) for i in range(lines_checked)]
        for i in range(lines_checked, img.shape[0]):
            row = bsum(img[i, :])
            if max(old) - min(old) <= precision and abs(row - sum(old)/lines_checked) > precision:
                rows.append(i)
            old = old[1:] + [row]

        old = [bsum(img[:, i]) for i in range(lines_checked)]
        for i in range(lines_checked, img.shape[1]):
            col = bsum(img[:, i])
            if max(old) - min(old) <= precision and abs(col - sum(old)/lines_checked) > precision:
                cols.append(i)
            old = old[1:] + [col]

        #make table of differences between lines
        row_freq = dict()
        col_freq = dict()
        for diff in [rows[i]-rows[i-1] for i in range(1, len(rows))]:
            if not diff in row_freq: row_freq[diff] = 0
            row_freq[diff] += 1
        for diff in [cols[i]-cols[i-1] for i in range(1, len(cols))]:
            if not diff in col_freq: col_freq[diff] = 0
            col_freq[diff] += 1

        # get most common difference between lines
        row_median_diff = [key for key, val in row_freq.items() if val == max(row_freq.values())][0]
        col_median_diff = [key for key, val in col_freq.items() if val == max(col_freq.values())][0]

        # insert lines at the edges
        if rows[0] != 0: rows.insert(0, 0)
        if cols[0] != 0: cols.insert(0, 0)
        if rows[-1] != img.shape[0]-1: rows.append(img.shape[0]-1)
        if cols[-1] != img.shape[1]-1: cols.append(img.shape[1]-1)

        # Fix missing lines
        i = 0
        while i < len(rows)-1:
            diff = rows[i+1] - rows[i]
            if diff > row_median_diff*1.3:
                rows.insert(i+1, rows[i+1]-row_median_diff)
            elif diff < row_median_diff*0.7:
                rows.remove(rows[i])
            else:
                i += 1
        i = 0
        while i < len(cols)-1:
            diff = cols[i+1] - cols[i]
            if diff > col_median_diff*1.3:
                cols.insert(i+1, cols[i+1]-col_median_diff)
            elif diff < col_median_diff*0.7:
                cols.remove(cols[i])
            else:
                i += 1

        # estimate each cell based on the average color of a square
        grid = []
        for r in range(1, len(rows)):
            row = []
            r0 = rows[r-1]; r1 = rows[r]
            for c in range(1, len(cols)):
                c0 = cols[c-1]; c1 = cols[c]
                avg = np.average(img[r0:r1, c0:c1])
                row.append(0 if avg < 0.5 else 1)
            grid.append(row)
            
        if self.show_info:
            print("QR-code loaded into reader")
            print(image_path, f"is {len(grid)}x{len(grid[0])} big\n")

        self.grid = grid


    def resetPos(self):
        self.bits_read = -1
        self.bytes_read = 0
        super().resetPos()


    def readBit(self):

        self.bits_read += 1

        if self.data:
            return self.data[self.bits_read]
        
        else:
            r, c = self.getNext()
            return self.grid[r][c]


    def readBits(self, n: int):
        """
            Returns bits as a number
        """
        return binaryFromBitlist([self.readBit() for _ in range(n)])


    def readByte(self):
        return self.readBits(8)


    def readBytes(self, n: int):
        """
            Returns list of bytes(int)

            Type: list[int]
        """
        return [self.readBits(8) for _ in range(n)]


    def getRawFormat(self): # returns 15 formatbits (still cooked)
        """
            Returns 15 formatbits as a list (still cooked)

            Type: list[int]
        """
        right = bottom = len(self.grid) - 1
        format = [self.grid[bottom - r][8] for r in range(7)] # 7 first bits
        format += [self.grid[8][right - 7 + c] for c in range(8)] # 8 remaining bits

        # cofirm it matches
        assert format == self.grid[8][0:6] + self.grid[8][7:9] + [self.grid[7][8]] + [r[8] for r in self.grid[0:6][::-1]]

        return format


    def getUncookedFormat(self):
        """
            Returns list of uncooked formatbits.
            (format_bits XOR 101010000010010)
        """

        format = self.getRawFormat()
        bits = binaryFromBitlist(format)
        bits = bits ^ 0b101010000010010 # XOR with static sequence
        uncooked = bitlistFromBinary(bits, 15)

        return uncooked


    def unMask(self, mask_indicator: int):
        assert self.isMasked == True

        mask = MASKS[mask_indicator]

        for r in range(len(self.grid)):
            for c in range(len(self.grid)):
                if mask(r, c) and self.valid[r][c]:
                    self.grid[r][c] ^= 1

        self.isMasked = False


    def decode(self):

        uncooked = self.getUncookedFormat()
        mask_indicator = binaryFromBitlist(uncooked[2:5])
        if self.show_info:
            print("Level", binaryFromBitlist(uncooked[:2]))
            print("Mask:", mask_indicator)
            print()

        # confirm 5 first bits matches with 10 parity bits
        assert confirmFormat(uncooked)

        self.unMask(mask_indicator)

        # confirm calculated error bytes match with actual error bytes
        assert checkForCorruption(self)

        message = []

        enc_mode = None
        while enc_mode != 0b0000: # terminator
            enc_mode = self.readBits(4)
            if self.show_info:
                print(f"Read enc-mode: {bin(enc_mode)} at bit position {self.bits_read}\n")

            match enc_mode:
                case 0b0001: # numeric
                    message.append(numeric_decoder(self))

                case 0b0010: # alphanumeric
                    message.append(alphanumeric_decoder(self))

                case 0b0100: # Byte
                    message.append(byte_decoder(self))

                # TODO finish kanji decoder 0b1000

                case 0b0111: # ECI
                    ECI_decoder(self)

                case _:
                    break
                    # raise ValueError(f"Cant find decoder for encoding mode: {bin(self.enc_mode)}")
                
        if self.show_info: print()
        print("Message:")
        print("".join(segment.replace("\r", "\n") for segment in message))


# TODO  1000 (Kanji) – Used for efficient encoding of Shift JIS characters, relevant for Japanese text.
#       0011 (Structured Append) – Allows splitting QR data across multiple symbols.
#       0101 (FNC1 Mode) – Needed for GS1/AI applications (like barcodes used in logistics and retail).

    
# example usage:

# Basic_reader("samples/hello_world.png").decode()