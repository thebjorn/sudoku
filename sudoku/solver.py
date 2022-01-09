
import os
from collections import defaultdict
from itertools import groupby
import json

DIRNAME = os.path.dirname(__file__)


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


class Steps(object):
    def __init__(self):
        self.steps = []

    def add(self, tag, board):
        self.steps.append([tag, board.__json__()])

    def show(self, outfname):
        with open(os.path.join(DIRNAME, 'board-template.html')) as fp:
            stepjson = json.dumps(self.steps, separators=(',', ':'))
            print("JSON:SIZE:", len(stepjson))
            html = fp.read().replace('$STEPS$', stepjson)

        with open(outfname, 'w') as fp:
            print(html, file=fp)
        os.startfile(outfname)


def solve(b, step_limit=100):
    actions = [NakedSingles(b), FindNakedTuples(b), HiddenSingles(b)]
    steps = Steps()

    steps.add('initial', b)
    # b.show_board('initial')
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
                steps.add(action.__class__.__name__, b)
                # b.show_board(f'{i}-{action.__class__.__name__}')
                break
        if b.solved():
            print("SOLVED :-)")
            steps.add('SOLVED', b)
            # b.show_board('SOLVED')
            return steps
        if not progress:
            print("NO_PROGRESS")
            break
    steps.add('no-solution', b)
    # b.show_board('no-solution')
    return steps
