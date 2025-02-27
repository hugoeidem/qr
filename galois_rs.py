

# ALPHA[n] = α^n mod (irreducible polynomial)
# α = 2
# ir. pol. = x^8 + x^4 + x^3 + x^2 + 1 = 0b100011101 = 285

ALPHA = list(range(256)) # GF(2^8)
LOG = list(range(256))

# first 8 digits are less than 255, 2^7 = 128
for i in range(8):
    ALPHA[i] = 1 << i

# α^i for i >= 8 are more than 255 and must be reduced
for i in range(8, 255):
    ALPHA[i] = ALPHA[i-1] * 2

    if ALPHA[i] > 255: 
        ALPHA[i] ^= 285 # XOR with irreducible polynomial

# the log table stores every exponent that results in which value
# e.g. LOG[α^n] = n
# LOG[0] is undefined since α^n >= 0
for i in range(255):
    LOG[ALPHA[i]] = i


class Poly:
    def __init__(self, alpha_exponants: list):
        """
            Create a polynomial from a list of alpha values where the first
            number in the list represents the exponent of the first alpha term 
            before the highest x term.
        """
        self.terms = alpha_exponants
        self.values = [ALPHA[a] for a in alpha_exponants]

    def deg(self):
        return len(self.terms) - 1

    def __mul__(self, other):
        # the amount of terms terms in the product will be the sum of the degrees + 1
        # set to 0 to allow XOR operation
        r = [0] * (self.deg() + other.deg() + 1)

        # index 0 represents the higest term
        for i, a in enumerate(self.terms):
            for j, b in enumerate(other.terms):

                # add the 
                new_exp = (a+b) % 255
                new_value = ALPHA[new_exp]

                # perform the multiplication (XOR)
                r[i + j] ^= new_value

        return Poly([LOG[i] for i in r]) 
    
    def __str__(self):
        return str(self.terms)


def polyECC(errorbytes: int) -> Poly:
    """
        Recursively calculates the generator polynomial based on the number of errorwords.

        returns: generator polynomial as Poly-class
    """
    if errorbytes == 1:
        return Poly([0, 0]) # start generator poly. (x + 1)
    
    tmp = polyECC(errorbytes - 1)
    
    # generate the polynomial by multiplicating the last poly with a^0x^1 + a^ix^0 where
    # i increases for every iteration starting at 1, meaning the gen poly [0, 1] (x + 2) 
    return tmp * Poly([0,errorbytes-1]) 


def rsBytes(message: list, error_words: int):
    """
        Returns a specified number of error bytes using reed solomon encoding
    """
    msg = message.copy()

    # get the generator polynomial
    gen = polyECC(error_words).terms # alpha notation

    times = len(msg)
    for _ in range(times):

        # if the first term is zero skip the division and just remove the first term
        if msg[0] == 0:
            msg = msg[1:]
            continue

        # multiply the generator poly by the coefficiant of the first term
        coef = LOG[msg[0]]

        g = [(i + coef)%255 for i in gen] 
        g = [ALPHA[i] for i in g] # back to integer notation

        # make sure both polynomials have the same amount of terms by padding with zeroes
        if len(msg) > len(g):
            g += [0] * (len(msg) - len(g))
        elif len(msg) < len(g):
            msg += [0] * (len(g) - len(msg))

        # perform the multiplication (XOR) and remove the first term since they will always be equal
        msg = [x^y for (x, y) in zip(msg, g)][1:]
    
    # the remainder is now the error correction bytes
    return msg


# TODO remove this
# correct results
dicti = {
    7: [1, 127, 122, 154, 164, 11, 68, 117],
    10: [1, 216, 194, 159, 111, 199, 94, 95, 113, 157, 193],
    13: [1, 137, 73, 227, 17, 177, 17, 52, 13, 46, 43, 83, 132, 120],
    15: [1, 29, 196, 111, 163, 112, 74, 10, 105, 105, 139, 132, 151, 32, 134, 26],
    16: [1, 59, 13, 104, 189, 68, 209, 30, 8, 163, 65, 41, 229, 98, 50, 36, 59],
    17: [1, 119, 66, 83, 120, 119, 22, 197, 83, 249, 41, 143, 134, 85, 53, 125, 99, 79],
    18: [
        1,
        239,
        251,
        183,
        113,
        149,
        175,
        199,
        215,
        240,
        220,
        73,
        82,
        173,
        75,
        32,
        67,
        217,
        146,
    ],
    20: [
        1,
        152,
        185,
        240,
        5,
        111,
        99,
        6,
        220,
        112,
        150,
        69,
        36,
        187,
        22,
        228,
        198,
        121,
        121,
        165,
        174,
    ],
    22: [
        1,
        89,
        179,
        131,
        176,
        182,
        244,
        19,
        189,
        69,
        40,
        28,
        137,
        29,
        123,
        67,
        253,
        86,
        218,
        230,
        26,
        145,
        245,
    ],
    24: [
        1,
        122,
        118,
        169,
        70,
        178,
        237,
        216,
        102,
        115,
        150,
        229,
        73,
        130,
        72,
        61,
        43,
        206,
        1,
        237,
        247,
        127,
        217,
        144,
        117,
    ],
    26: [
        1,
        246,
        51,
        183,
        4,
        136,
        98,
        199,
        152,
        77,
        56,
        206,
        24,
        145,
        40,
        209,
        117,
        233,
        42,
        135,
        68,
        70,
        144,
        146,
        77,
        43,
        94,
    ],
    28: [
        1,
        252,
        9,
        28,
        13,
        18,
        251,
        208,
        150,
        103,
        174,
        100,
        41,
        167,
        12,
        247,
        56,
        117,
        119,
        233,
        127,
        181,
        100,
        121,
        147,
        176,
        74,
        58,
        197,
    ],
    30: [
        1,
        212,
        246,
        77,
        73,
        195,
        192,
        75,
        98,
        5,
        70,
        103,
        177,
        22,
        217,
        138,
        51,
        181,
        246,
        72,
        25,
        18,
        46,
        228,
        74,
        216,
        195,
        11,
        106,
        130,
        150,
    ]
}

# # PRINT VALUES COMPARED WITH REAL GOOD RESULT
# for error_words, pol in dicti.items():
#     print(error_words, pol == polyECC(error_words).values)
#     print(pol)
#     print(polyECC(error_words).values) 
#     print()


