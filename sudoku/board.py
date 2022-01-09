import os
from collections import defaultdict
from itertools import groupby

DIRNAME = os.path.dirname(__file__)


class Cell(object):
    def __init__(self, data=None, index=0):
        self.possibilities = data if data is not None else list(range(1, 10))
        self.row = index // 9
        self.column = index % 9
        self.box = 3*(index // (9*3)) + (index % 9 // 3)
        self.digit = self.possibilities[0] if len(self.possibilities) == 1 else 0

    def set_value(self, n):
        self.digit = n
        self.possibilities = [n]

    def xy(self):
        return (self.row, self.column)

    def has_digit(self):
        return self.digit != 0
        # return len(self.possibilities) == 1

    def can_see(self, other):
        if self is other:
            return False
        return self.row == other.row or self.column == other.column or self.box == other.box

    # @property
    # def digit(self):
    #     return self.possibilities[0] if self.has_digit() else 0

    def remove_possibility(self, n):
        if self.has_digit():
            return False
        if n in self.possibilities:
            self.possibilities.remove(n)
            if self.has_digit():
                print(f"XXX found naked single {self.digit} in ({repr(self)})")
            return True
        return False

    def remove_possibilities(self, lst):
        res = set()
        for val in lst:
            if self.remove_possibility(val):
                res.add(val)
        return res

    def __len__(self):
        return len(self.possibilities)

    def possibilities_string(self):
        return ''.join(sorted(set(map(str, self.possibilities))))

    def __eq__(self, other):
        # print(self, other, type(self), type(other))
        return set(self.possibilities) == set(other.possibilities)

    def as_html(self):
        n = len(self.possibilities)
        # dbgstr = f'<span class="debug">{repr(self)}</span>'
        dbgstr = ''
        if n == 0:
            return '<td class="error"></td>'
        elif n == 1 and self.has_digit():
            return f'<td class="digit">{self.digit}{dbgstr}</td>'
        else:
            def box2html(bx):
                res = ['<table class="options">']
                for y in range(3):
                    res.append('<tr>')
                    for n in range(y*3, (y+1)*3):
                        if n+1 in self.possibilities:
                            res.append(f'<td>{n+1}</td>')
                        else:
                            res.append('<td>&nbsp;</td>')
                    res.append('</tr>')
                res.append('</table>')
                return '\n'.join(res)


            return f'''
                <td class="possibilities">
                    {box2html(self.possibilities)}
                    {dbgstr}
                </td>
            '''

    def __str__(self):
        return str(self.digit)

    def __repr__(self):
        return f'r{self.row+1}c{self.column+1}={"".join(map(str,self.possibilities))}'


class BoardData(object):
    def __init__(self, data='0' * 9 * 9):
        self.data = data.replace('.', '0')

    def __getitem__(self, key):
        return int(self.data[key])

    def possibilites(self, n):
        v = self[n]
        if v == 0:
            return list(range(1, 10))
        return [v]

    def __repr__(self):
        rows = []
        for i in range(9):
            rows.append(' '.join(self.data[i*9: (i+1)*9]))
        return '\n'.join(rows)


class Area(object):
    def __init__(self, cells):
        self.cells = cells


class Board(object):
    def __init__(self, board_data=None):
        #: all cells in row-major order r1c1, r1c2, ..., r1c9, r2c1, r2c2, etc.
        # self.cells = [Cell([(i%9)+1]) for i in range(9*9)]
        if board_data is not None:
            self.cells = [Cell(board_data.possibilites(i), index=i) for i in range(9*9)]
        else:
            self.cells = [Cell(index=i) for i in range(9*9)]

        #: 9 boxes with 9 cells in each
        self.boxes = [[] for i in range(9)]

        #: 9 columns with 9 cells in each
        self.cols = [[] for i in range(9)]

        #: 9 rows with 9 cells in each
        self.rows = [[] for i in range(9)]

        for cell in self.cells:
            self.boxes[cell.box].append(cell)
            self.cols[cell.column].append(cell)
            self.rows[cell.row].append(cell)

        self.cells_with_digits = set()
        self.cleanup()

    def areas(self):
        return self.boxes + self.cols + self.rows

    def solved(self):
        for area in self.areas():
            if not all(c.has_digit() for c in area):
                # print("NOT_SOLVED(has-digit):", [repr(c) for c in area])
                return False
            if {c.digit for c in area} != set(range(1, 10)):
                # print("NOT_SOLVED(1-9):", [repr(c) for c in area])
                return False
        return True

    def cleanup_cell(self, cell, report=False):
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

    def as_html(self):
        def box2html(bx):
            res = ['<table class="inner">']
            for y in range(3):
                res.append('<tr>')
                for cell in bx[y*3: (y+1)*3]:
                    res.append(cell.as_html())
                res.append('</tr>')
            res.append('</table>')
            return '\n'.join(res)

        res = []
        for y in range(3):
            res.append('<tr>')
            for bx in self.boxes[y*3: (y+1)*3]:
                res.append('<td>')
                res.append(box2html(bx))
                res.append('</td>')
            res.append('</tr>')
        html_board = '\n'.join(res)

        with open(os.path.join(DIRNAME, 'board-template.html')) as fp:
            return fp.read().replace('$SUDOKU_BOARD$', html_board)


class Action(object):
    def __init__(self, board):
        self.board = board

    def run(self):
        return False  # no progress


def noop(*args, **kwargs):
    pass


class NakedSingles(Action):
    def __init__(self, board):
        super().__init__(board)
        self.seen_digits = set()

    def run(self, print=print):
        progress = False
        for cell in self.board.cells:
            if not cell.has_digit() and len(cell.possibilities) == 1:
                cell.set_value(cell.possibilities[0])
                progress = True
                print(f"found naked single in {repr(cell)}")
                self.board.cleanup_cell(cell, report=True)
                return True
        return progress


class HiddenSingles(Action):
    def run(self):
        progress = False
        for area in self.board.areas():
            digits = defaultdict(set)
            known_digits = set()
            for i, cell in enumerate(area):
                if cell.has_digit():
                    known_digits.add(cell.digit)
                    continue
                for n in cell.possibilities:
                    digits[n].add(i)
            for n, cells in digits.items():
                if n in known_digits:
                    continue
                if len(cells) == 1:
                    i, = cells
                    cell = area[i]
                    progress = True
                    cell.set_value(n)
                    print(f"found hidden single ({n}) in {repr(cell)}")
                    self.board.cleanup_cell(cell, report=True)
                    return True
        return progress


class FindNakedTuples(Action):
    def __init__(self, board):
        super().__init__(board)
        self.seen_tuples = set()

    def run(self):
        progress = False
        for area in self.board.areas():
            tuples = set()
            for key, it in groupby(sorted(area, key=lambda cell: cell.possibilities_string()), lambda cell: cell.possibilities_string()):
                cells = list(it)
                ntuple = tuple(map(int, list(key)))
                tmp = (key, tuple(c.xy() for c in cells))
                if tmp in self.seen_tuples:
                    continue
                tuples.add(tmp)
                if len(cells) > 1 and len(key) == len(cells):
                    output = [f"found naked {len(cells)}-tuple ({key}) in {cells}"]
                    for c in area:
                        if c not in cells:
                            curval = repr(c)
                            removed_vals = c.remove_possibilities(ntuple)
                            if removed_vals:
                                progress = True
                                output.append(f"removed {', '.join(map(str, sorted(removed_vals)))} from {curval}")
                    self.seen_tuples.add(tmp)
                    if progress:
                        print('\n'.join(output))
                        return True
            self.seen_tuples |= tuples
        return progress        


def print_board(b, index):
    fname = f'tmp-{index}.html'
    with open(fname, 'w') as fp:
        print(b.as_html(), file=fp)
    os.startfile(fname)


def solve(b, step_limit=100):
    actions = [NakedSingles(b), FindNakedTuples(b), HiddenSingles(b)]
    print_board(b, 'initial')
    i = 0
    while 1:
        i += 1
        print(f'step {i}------------------------')
        if i > step_limit:
            print(f"i>{step_limit}")
            break
        progress = False
        for action in actions:
            action_progress = action.run()
            progress = progress or action_progress
            b.cleanup()
            if action_progress:
                print_board(b, f'{i}-{action.__class__.__name__}')
                break
        if b.solved():
            print("SOLVED :-)")
            print_board(b, 'SOLVED')
            return b
        if not progress:
            print("NO_PROGRESS")
            break
    print_board(b, 'no-solution')
    return b

if __name__ == "__main__":
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

    b = Board(dtfeb19)
    b = solve(b)
