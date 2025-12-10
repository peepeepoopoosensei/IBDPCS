# select square + 0 fill
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
