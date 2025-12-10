# select square + 0 fill
from collections import deque
def select_square(self, x=None, y=None, cell=None):
    """
    Reveal a cell by coordinates (x,y) or by passing a Cell via cell=.
    If the cell's number is 0, reveal all connected zeroes and their
    bordering numbered cells (BFS).
    Returns a list of cells that were newly revealed.
    """
    if cell is None:
        if x is None or y is None:
            raise ValueError("Provide either x,y or cell")
        cell = self.grid[y][x]

    # If already revealed or flagged, do nothing
    if cell.revealed or cell.isFlagged:
        return []

    # If it's a bomb: reveal and return it (game logic can handle loss)
    if cell.isBomb:
        cell.revealed = True
        return [cell]

    revealed_cells = []
    # Reveal the start cell
    cell.revealed = True
    revealed_cells.append(cell)

    # If the cell has a number > 0, we stop here
    if cell.num != 0:
        return revealed_cells

    # BFS queue for flood fill of zero-cells and their neighbors
    q = deque([cell])
    while q:
        cur = q.popleft()
        for n in self.neighbors(cur):
            # Skip bombs and flagged cells and already revealed cells
            if n.isBomb or n.isFlagged or n.revealed:
                continue

            # Reveal this neighbor
            n.revealed = True
            revealed_cells.append(n)

            # If neighbor is zero, add to queue to expand further
            if n.num == 0:
                q.append(n)

    return revealed_cells


def print_board(board, show_bombs=False):
    """
    Print a simple textual representation:
      - unrevealed: '#'
      - revealed 0: ' '
      - revealed >0: digit
      - bomb (if show_bombs True): '*'
    """
    for y in range(board.height):
        row = []
        for x in range(board.width):
            c = board.grid[y][x]
            if c.revealed:
                if c.isBomb:
                    ch = '*'
                else:
                    ch = ' ' if c.num == 0 else str(c.num)
            else:
                ch = '*' if (show_bombs and c.isBomb) else '#'
            row.append(ch)
        print(' '.join(row))
    print()
