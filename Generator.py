import random


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
            return 9
        return sum(1 for neighbor in self.board.neighbors(self) if neighbor.isBomb)
        # adds 1 to total if neighbour is bomb, using neighbours() method to yield all neighbours


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
        self.place_bombs(first_selection)

    def neighbors(self, cell):  # r
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
