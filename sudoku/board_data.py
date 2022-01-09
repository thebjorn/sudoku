
class BoardData(object):
    """Simple class to read in sudoku board data in a semi-standard format.
    
       Usage (reading in data for the dtfeb19 puzzle at 
       https://sandiway.arizona.edu/sudoku/examples.html)::

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

       Note that there are no commas. Python concatinates consecutive strings,
       and putting the string over 9 lines mirrors the grid layout of the 
       sudoku.

    """
    def __init__(self, data='0' * 9 * 9):
        self.data = data.replace('.', '0')

    def __getitem__(self, key):
        """Implement ``self[key]`` and return the value as an int.
        """
        return int(self.data[key])

    def possibilites(self, n):
        """Return the posibilities for position ``n``.
           It's either the digit from the input string
           or the list [1,2,3,4,5,6,7,8,9]
        """
        v = self[n]
        if v == 0:
            return list(range(1, 10))
        return [v]

    def __repr__(self):
        rows = []
        for i in range(9):
            rows.append(' '.join(self.data[i*9: (i+1)*9]))
        return '\n'.join(rows)
