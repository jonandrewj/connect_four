import numpy
import random

BLACK = 1
RED = -1

COLUMNS = 7
ROWS = 6

class Board:
    def __init__(self):
        self.grid = numpy.zeros((COLUMNS, ROWS))
        self.playable_columns = None
        self.last_placement = None

    def place(self, column, color):
        #if not 0 <= column < COLUMNS:
        #    raise ValueError('Invalid column index ' + str(column))
        #if color != BLACK and color != RED:
        #    raise ValueError('Invlalid piece color ' + str(color))

        row = 0
        while row < ROWS and self.grid[column][row] != 0:
            row += 1

        if row == ROWS:
            return 'Cant play in this column because it is full'

        if self.playable_columns != None and row == ROWS-1:
            self.playable_columns.remove(column)

        self.grid[column][row] = color
        return None

    def unplace(self, column):
        row = ROWS - 1
        while self.grid[column][row] == 0:
            row -= 1

        self.grid[column][row] = 0
        
        if row == ROWS - 1 and self.playable_columns != None:
            self.playable_columns.append(column)

    def winner(self, column, row):
        color = self.grid[column][row]
        if color not in [RED, BLACK]:
            return None

        # VERTICAL
        if row >= 3:
            if (self.grid[column][row-1] == color and
                self.grid[column][row-2] == color and
                self.grid[column][row-3] == color):
                return color
        # HORIZONTAL
        if column <= 3:
            if (self.grid[column+1][row] == color and
                self.grid[column+2][row] == color and
                self.grid[column+3][row] == color):
                return color
        # DIAGONAL DOWNWARDS
        if column <= 3 and row >= 3:
            if (self.grid[column+1][row-1] == color and
                self.grid[column+2][row-2] == color and
                self.grid[column+3][row-3] == color):
                return color
        # DIAGONAL UPWARDS
        if column <= 3 and row <= 2:
            if (self.grid[column+1][row+1] == color and
                self.grid[column+2][row+2] == color and
                self.grid[column+3][row+3] == color):
                return color
        return None

    def finished(self):
        # HORIZONTAL
        for col in range(COLUMNS-3):
            for row in range(ROWS):
                color = self.grid[col][row]
                if (color != 0 and
                    self.grid[col+1][row] == color and
                    self.grid[col+2][row] == color and
                    self.grid[col+3][row] == color):
                    return color
        # VERTICAL
        for col in range(COLUMNS):
            for row in range(ROWS-3):
                color = self.grid[col][row]
                if (color != 0 and
                    self.grid[col][row+1] == color and
                    self.grid[col][row+2] == color and
                    self.grid[col][row+3] == color):
                    return color

        # DIAGONAL UPWARDS
        for col in range(COLUMNS-3):
            for row in range(ROWS-3):
                color = self.grid[col][row]
                if (color != 0 and
                    self.grid[col+1][row+1] == color and
                    self.grid[col+2][row+2] == color and
                    self.grid[col+3][row+3] == color):
                    return color

        # DIAGONAL DOWNWARDS
        for col in range(COLUMNS-3):
            for row in range(3, ROWS):
                color = self.grid[col][row]
                if (color != 0 and
                    self.grid[col+1][row-1] == color and
                    self.grid[col+2][row-2] == color and
                    self.grid[col+3][row-3] == color):
                    return color

        if (self.grid == 0).any():
            return None

        return 0

    def won(self, col, color):
        row = ROWS-1
        while self.grid[col][row] == 0:
            row -= 1

        # DOWN
        if (row >= 3 and 
            self.grid[col][row-1] == color and
            self.grid[col][row-2] == color and
            self.grid[col][row-3] == color):
            return True

        # HORIZONTAL
        right_col = col+1
        right_count = 0
        while right_col < COLUMNS and self.grid[right_col][row] == color:
            right_count += 1
            right_col += 1

        left_col = col-1
        left_count = 0
        while left_col >= 0 and self.grid[left_col][row] == color:
            left_count += 1
            left_col -= 1

        if right_count + left_count >= 3:
            return True

        # UPWARD DIAGONAL
        r_col = col+1
        r_row = row+1
        r_count = 0
        while (r_col < COLUMNS and r_row < ROWS and self.grid[r_col][r_row] == color):
            r_col += 1
            r_row += 1
            r_count += 1

        l_col = col-1
        l_row = row-1
        l_count = 0
        while (l_col >= 0 and l_row >= 0 and self.grid[l_col][l_row] == color):
            l_col -= 1
            l_row -= 1
            l_count += 1

        if r_count + l_count >= 3:
            return True

        # DOWNWARD DIAGONAL
        r_col = col+1
        r_row = row-1
        r_count = 0
        while (r_col < COLUMNS and r_row >= 0 and
            self.grid[r_col][r_row] == color):
            r_col += 1
            r_row -= 1
            r_count += 1

        l_col = col-1
        l_row = row+1
        l_count = 0
        while (l_col >= 0 and l_row < ROWS and
            self.grid[l_col][l_row] == color):
            l_col -= 1
            l_row += 1
            l_count += 1

        if r_count + l_count >= 3:
            return True

        return False

    def copy(self):
        copy = Board()
        copy.grid = self.grid.copy()
        return copy

    def get_grid(self, color):
        copy = self.grid.copy()
        if color == RED:
            copy = copy * -1
        return copy

    def get_playable_columns(self):
        if self.playable_columns == None:
            playable = []
            for col in range(COLUMNS):
                if self.grid[col][ROWS-1] == 0:
                    playable.append(col)
            self.playable_columns = playable

        return self.playable_columns

        

        