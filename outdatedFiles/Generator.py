import random
from collections import deque


class Cell:
    def __init__(self, board, x, y):
        # initialising
        self.board = board
        self.x = x
        self.y = y
        self.isBomb = False
        self.isFlagged = False
        self.revealed = False

    """the decorator @property makes the next method’s output a
    property of the object, which is assigned only when needed 
    and updates dynamically"""
    @property
    def num(self):
        if self.isBomb:
            return '*'
        return sum(1 for neighbor in self.board.neighbors(self) if neighbor.isBomb)
        # adds 1 to total if neighbour is bomb, using neighbours() method to yield all neighbours
    
    @property
    def isUnknown(self):
            return not self.revealed and not self.isFlagged

    @property
    def isNumber(self):
            return self.revealed and not self.isBomb


class Board:
    def __init__(self, width, height, bomb_count, first_selection):
        self.width = width
        self.height = height
        self.bomb_count = bomb_count
        self.first_selection = first_selection
        self.grid = [
            [Cell(self, x, y) for x in range(width)]
            for y in range(height)
        ]  # generates as many cell objects as needed for specified size
        self.place_bombs(first_selection)  # place bombs method
        self._initial_zero_expand()  # zero expand method

    def neighbors(self, cell):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:  # if middle value (selected cell), skip
                    continue
                nx, ny = cell.x + dx, cell.y + dy  # gives coords of current checked cell
                # checks that the current cell we are checking is within bounds of the grid
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # yield is like return but continues instead of ending the function
                    yield self.grid[ny][nx]

    def place_bombs(self, first_selection):
        fx, fy = first_selection

        # Build the list of positions where bombs could be placed
        candidates = []

        for y in range(self.height):
            for x in range(self.width):

                # Skip the first selection itself
                # Skip neighbors of the first click and reveal them
                if (x, y) == (fx, fy) or (abs(x - fx) <= 1 and abs(y - fy) <= 1):
                    # reveal the first selection and neighbours
                    self.grid[y][x].revealed = True
                    continue

                candidates.append((x, y))

        # Randomly select bomb positions
        bomb_positions = random.sample(candidates, self.bomb_count)

        # Mark the cells as bombs
        for (x, y) in bomb_positions:
            self.grid[y][x].isBomb = True

    def _initial_zero_expand(self):
        q = deque()

        # Start BFS from any revealed zero-cell in the 3×3 initial region
        fx, fy = self.first_selection

        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = fx + dx, fy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    c = self.grid[ny][nx]
                    if not c.isBomb and c.num == 0:
                        q.append(c)

        seen = set()

        while q:
            cur = q.popleft()
            if cur in seen:
                continue
            seen.add(cur)

            # Expand neighbors
            for n in self.neighbors(cur):
                # Reveal safe neighbors only
                if not n.isBomb and not n.revealed:
                    n.revealed = True

                # Continue expansion only through zero cells
                if not n.isBomb and n.num == 0 and n not in seen:
                    q.append(n)

    
    def print_board(self, show_bombs=False):
        for y in range(self.height):
            row = []
            for x in range(self.width):
                c = self.grid[y][x]
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

