
from Generator import Board  # your solver file

class Solver:
     def __init__(self, board):
          self.num_bombs = 0
          self.board = board
          self.outdated = []  # collection of outdated numbered cells

     def initialize(self):
          # build solver_grid from board.revealed status --> what do you mean by this???
          # build initial outdated list
          for i in range(self.board.height):
               for j in range(self.board.width):
                    cell = self.board.grid[i][j]
                    if cell not in self.outdated and cell.revealed and not cell.isBomb and any((not x.revealed and not x.isFlagged)for x in self.board.neighbors(cell)):
                         self.outdated.append(cell)

     def run(self):
          # loops to analyse cells in the outdated pile and deletes them after the analysis until there are no outdated cells in the pile (no more changes have occurred)
          while self.outdated:
               # pick one cell, delete it & analyse it
               cell = self.outdated.pop(0)
               self.analyseCell(cell)
          print("Finished")


     def analyseCell(self, cell):
          neighbors = list(self.board.neighbors(cell))
          n = cell.num # number of bombs around
          f = sum(1 for x in neighbors if x.isFlagged)
          u = sum(1 for x in neighbors if not x.revealed and not x.isFlagged)
          # apply MAIN RULES
          if n - f < 0 or n - f > u:
               print("Error")
          elif n - f == u:
               # all remaining unknowns must be bombs (flagged)
               for i in range(len(neighbors)):
                    if neighbors[i].isUnknown:
                         changed_cell = neighbors[i]
                         changed_cell.isFlagged = True
                         # adds affected neighboring numbered cells to the outdated pile
                         adjacents = list(self.board.neighbors(changed_cell))
                         for j in range(len(adjacents)):
                              if adjacents[j].isNumber and adjacents[j] not in self.outdated:
                                   self.outdated.append(adjacents[j])
          elif  n == f:
               # all remaining unknowns must be safe
               for i in range(len(neighbors)):
                    if neighbors[i].isUnknown:
                         changed_cell = neighbors[i]
                         changed_cell.revealed = True
                         # adds affected neighboring numbered cells to the outdated pile
                         adjacents = list(self.board.neighbors(changed_cell))
                         for j in range(len(adjacents)):
                              if adjacents[j].isNumber and adjacents[j] not in self.outdated:
                                   self.outdated.append(adjacents[j])

# Output the board as viewed by the solver
     def print_solver_view(self):
          for y in range(self.board.height):
               row = []
               for x in range(self.board.width):
                    cell = self.board.grid[y][x]
                    if cell.isFlagged:
                         row.append("💥")
                         self.num_bombs += 1
                    elif cell.revealed:
                         row.append(str(cell.num))
                    else:
                         row.append("?")
               print(" ".join(row))
          print()
          print(f"Number of BOMBS found: {self.num_bombs} out of {self.board.bomb_count}")
          print()

# ---- TEST SETUP ----

first_click = (2, 3)
board = Board(20, 20, 15, first_click)

print("REAL BOARD (with bombs hidden):")
board.print_board(show_bombs=False)

print("REAL BOARD (with bombs visible - DEBUG):")
board.print_board(show_bombs=True)

solver = Solver(board)

print("INITIAL SOLVER VIEW:")
solver.print_solver_view()


solver.initialize()
solver.run()

print("FINAL SOLVER VIEW:")


solver.print_solver_view()

print("FINAL REAL BOARD (DEBUG):")
board.print_board(show_bombs=True)
