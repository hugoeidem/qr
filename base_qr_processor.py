

from functions import print2dArray, getValidPositions


class BaseQRProcessor:
    def __init__(self, version: int, grid: list): # version starts at 0
        self.version = version
        self.grid = grid
        
        # TODO valid needs to be generated from a function so 40 versions arent needed
        self.valid = getValidPositions(self.version) # version 1 = 0
        self.up = self.left = True
        self.pos = len(grid)-1, len(grid)-1

    def print(self, message=None): # input is 2d-array
        if message: print(message)
        print2dArray(self.grid)

    def getNext(self):
        """
            Returns next position in the QR grid.
        """

        r, c = self.pos

        if c == 6: # the dotted left line screws up the ziczac
            self.left = True
            self.pos = r, 5
            return self.getNext()

        if self.left: # should go left
            self.pos = r, c-1 # move left

        elif self.up: # should go up
            if r == 0: # but at the top
                self.pos = r, c-1 # move left instead
                self.up = False
            else: # not at the top
                self.pos = r-1, c+1 # move ziczac up right

        else: # should go down
            if r == len(self.grid)-1: # but at the bottom
                self.pos = r, c-1 # move left instead
                self.up = True
            else: # not at the bottom
                self.pos = r+1, c+1 # move ziczac down right

        self.left = not self.left
            
        if self.valid[r][c]:
            return r, c
        else:
            return self.getNext()

    def resetPos(self):
        self.left = self.up = True
        self.pos = len(self.grid)-1, len(self.grid)-1