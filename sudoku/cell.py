

class Cell(object):
    """Each cell is indexed from 0..80 to make it easy to figure out which
       row, column, and box it belongs to.

       See the Board class for how this is used.
    """
    def __init__(self, data=None, index=0):
        # set possibilities to [1,2,3,4,5,6,7,8,9] or data
        # data must be a list if it is given
        self.possibilities = data if data is not None else list(range(1, 10))
        self.row = index // 9
        self.column = index % 9
        self.box = 3*(index // (9*3)) + (index % 9 // 3)
        # set the value (digit) of this cell to 0 (unknown) unless we 
        # only have one possibility
        self.digit = self.possibilities[0] if len(self.possibilities) == 1 else 0

    def set_value(self, n):
        """Set the value (digit) of this cell.
        """
        self.digit = n
        self.possibilities = [n]

    def xy(self):
        """Convenience method to return the row/column of the cell as a tuple.
        """
        # this is used in Board.cells_with_digits        
        return (self.row, self.column)

    def has_digit(self):
        """Does this cell have a digit?"""        
        return self.digit != 0

    def can_see(self, other):
        """Can this cell see the other cell?
        """
        if self is other:
            return False
        return self.row == other.row or self.column == other.column or self.box == other.box

    def remove_possibility(self, n):
        """Returns True if ``n`` can be removed from the possibilities in 
           this cell.
        """
        if self.has_digit():
            return False
        if n in self.possibilities:
            self.possibilities.remove(n)
            if self.has_digit():
                print(f"XXX found naked single {self.digit} in ({repr(self)})")
            return True
        return False

    def remove_possibilities(self, lst):
        """Returns a set of digits (from lst) that were removed from this cell.
        """
        res = set()
        for val in lst:
            if self.remove_possibility(val):
                res.add(val)
        return res

    # def __len__(self):
    #     return len(self.possibilities)

    def possibilities_string(self):
        return ''.join(sorted(set(map(str, self.possibilities))))

    def __eq__(self, other):
        # print(self, other, type(self), type(other))
        return set(self.possibilities) == set(other.possibilities)

    def __json__(self):
        if self.has_digit():
            return self.digit
        else:
            return self.possibilities[:]  # return a copy

    def __str__(self):
        return f'r{self.row+1}c{self.column+1}'

    def __repr__(self):
        return f'r{self.row+1}c{self.column+1}={"".join(map(str,self.possibilities))}'
