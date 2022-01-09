import os

from board_data import BoardData
from cell import Cell

DIRNAME = os.path.dirname(__file__)



class Board(object):
    def __init__(self, board_data=None):
        #: all cells in row-major order r1c1, r1c2, ..., r1c9, r2c1, r2c2, etc.
        # send the index of the cell to Cell(...) so it can figure out 
        # which row/column/box it belongs to.
        self.cells = [Cell(board_data.possibilites(i), index=i) for i in range(9*9)]

        # define the areas of the grid: rows, columns and boxes...

        #: 9 boxes with 9 cells in each
        self.boxes = [[] for i in range(9)]

        #: 9 columns with 9 cells in each
        self.cols = [[] for i in range(9)]

        #: 9 rows with 9 cells in each
        self.rows = [[] for i in range(9)]

        # the cells know which row/column/box they belong to, so just append
        for cell in self.cells:
            self.boxes[cell.box].append(cell)
            self.cols[cell.column].append(cell)
            self.rows[cell.row].append(cell)

        self.cells_with_digits = set()  # cells that contain digits
        self.cleanup()                  # cleanup fills cells_with_digits

    def __json__(self):
        # return BoardData(''.join(map(str, [self.cells[i].digit for i in range(9*9)])))
        return [c.__json__() for c in self.cells]

    def areas(self):
        """Returns a list containing all boxes, columns and rows.
           (a list of 9+9+9=27 lists, each containing 9 cells, a cell is shared
           between 3 of the sub-lists)
        """
        return self.boxes + self.cols + self.rows

    def solved(self):
        """Returns True iff the grid is solved.
        """
        for area in self.areas():
            # all the cells in an area (box/column/row) must have a digit
            if not all(c.has_digit() for c in area):
                # print("NOT_SOLVED(has-digit):", [repr(c) for c in area])
                return False
            # every area (box/column/row) must contain the digits 1..9
            if {c.digit for c in area} != set(range(1, 10)):
                # print("NOT_SOLVED(1-9):", [repr(c) for c in area])
                return False
        return True

    def cleanup_cell(self, cell, report=False):
        """Remove the digit in ``cell`` from the possibilities of all the other
           cells that it can see.
        """        
        assert cell.has_digit()
        self.cells_with_digits.add(cell.xy())
        for c in self.cells:
            if c.has_digit():
                continue
            if cell.can_see(c):
                curval = repr(c)
                if c.remove_possibility(cell.digit):
                    if report:
                        print(f"removed {cell.digit} from {curval}")

    def cleanup(self):
        """For all cells that have digits, remove the digit from all other 
           cells that it can see (i.e. same box, row, or column).
        """
        for cell in self.cells:
            if not cell.has_digit() or cell.xy() in self.cells_with_digits:
                continue
            self.cleanup_cell(cell)

    def digits(self):
        return [c for c in self.cells if c.has_digit()]

    def as_data(self):
        return BoardData(''.join(map(str, [self.cells[i].digit for i in range(9*9)])))

    def __getitem__(self, pos):
        x, y = pos
        return self.cells[y*9 + x]


if __name__ == "__main__":
    from solver import solve
    # dtfeb19
    dtfeb19 = BoardData(
        '.2.6.8...'
        '58...97..'
        '....4....'
        '37....5..'
        '6.......4'
        '..8....13'
        '....2....'
        '..98...36'
        '...3.6.9.')

    wildcatjan17 = BoardData(
        '...26.7.1'
        '68..7..9.'
        '19...45..'
        '82.1...4.'
        '..46.29..'
        '.5...3.28'
        '..93...74'
        '.4..5..36'
        '7.3.18...'
    )
    challenge1 = BoardData(
        '.2.......'
        '...6....3'
        '.74.8....'
        '.....3..2'
        '.8..4..1.'
        '6..5.....'
        '....1.78.'
        '5....9...'
        '.......4.'
    )

    # b = Board(dtfeb19)
    # b = Board(wildcatjan17)
    b = Board(challenge1)
    steps = solve(b)
    steps.show('dtfeb19.html')
    print('done')
