
from Generator import Board
from collections import deque


class Solver:
     def __init__(self, board):
          self.num_bombs = 0
          self.board = board
          # collection of outdated numbered cells
          self.outdated_q = deque()  # queue of cells to process
          self.outdated_set = set()  # membership check (no duplicates)
     
     # helper functions for outdated queue/set
     def enqueue_outdated(self, cell):
          if cell not in self.outdated_set:
               self.outdated_q.append(cell)
               self.outdated_set.add(cell)

     def dequeue_outdated(self):
          cell = self.outdated_q.popleft()
          self.outdated_set.remove(cell)
          return cell
     
     # build the notation for a cell
     def cell_notation(self, cell):
          neighbors = list(self.board.neighbors(cell))
          n = cell.num
          f = sum(1 for nb in neighbors if nb.isFlagged)
          U = {nb for nb in neighbors if nb.isUnknown}
          u = len(U)
          b = n - f
          return neighbors, n, f, U, u, b
     
     # flag a cell and add affected num. cells to outdated pile
     def flagCell(self, c):
          assert c.isUnknown  # catches mistakes during development
          c.isFlagged = True
          # adds affected adjacent numbered cells to the outdated pile
          adjacents = self.board.neighbors(c)
          for adj in adjacents:
               if adj.isNumber:
                    self.enqueue_outdated(adj)

     # reveal a cell and add affected num. cells to the outdated pile
     def revealCell(self, c):
          assert c.isUnknown  # catches mistakes during development
          c.revealed = True
          # enqueue the revealed cell itself
          if c.isNumber and any(nb.isUnknown for nb in self.board.neighbors(c)):
               self.enqueue_outdated(c)
          # adds affected neighbouring numbered cells to the outdated pile
          adjacents = self.board.neighbors(c)
          for adj in adjacents:
               if adj.isNumber:
                    self.enqueue_outdated(adj)

     def singleCellAnalysis(self, cell):
          # initialise variables & CO.
          neighbors, n, f, U, u, b = self.cell_notation(cell)
          # apply conditions
          if b < 0 or b > u:
               print("ERROR: b (number of remaining bombs around num. cell (n - f)) is not in the right range")
               return False
          elif b == u and u > 0:
               # all remaining unknowns must be bombs (flagged)
               for changed_cell in U:
                    self.flagCell(changed_cell)
               return True
          elif  b == 0 and u > 0:
               # all remaining unknowns must be safe
               for changed_cell in U:
                    self.revealCell(changed_cell)
               return True
          return False

     def multiCellAnalysis(self, cell):
          # initialise variables & CO.
          neighbors, n_A, f_A, U_A, u_A, b_A = self.cell_notation(cell)
          if u_A == 0:
               return False
          B = {nb for u_cell in U_A for nb in self.board.neighbors(u_cell) if nb.isNumber and nb is not cell}
          # iterate over each candidate
          for cell_B in B:
               neighbors, n_A, f_A, U_A, u_A, b_A = self.cell_notation(cell)  # refresh A each time
               neighbors_B, n_B, f_B, U_B, u_B, b_B = self.cell_notation(cell_B)
               if u_B == 0:
                    continue
          # compare sizes
               if u_A <= u_B:
                    U_small, b_small = U_A, b_A
                    U_large, b_large = U_B, b_B
               else:
                    U_small, b_small = U_B, b_B
                    U_large, b_large = U_A, b_A
               # apply conditions
               if b_small < 0 or b_small > len(U_small) or b_large < 0 or b_large > len(U_large):
                    print("ERROR: b (number of remaining bombs around num. cell (n - f)) is not in the right range")
               elif U_small < U_large:
                    D = U_large - U_small
                    if not D:
                         continue
                    k = b_large - b_small
                    if k < 0:
                         print("ERROR: k (bombs that must live in D) cannot be negative")
                         continue
                    if k == len(D):  # all cells in D are bombs
                         # flag all cells in D and enqueue in outdated, for each flagged cell, its adjacent numbered cells
                         for c in D: self.flagCell(c)
                         return True
                    elif k == 0:  # all cells in D are safe
                         # reveal all cells in D and enqueue in outdated, for each revealed cell, itself if numbered and its adjacent numbered cells
                         for c in D: self.revealCell(c)
                         return True
          return False

     def analyseCell(self, cell):
          # SINGLE-CELL ANALYSIS
          self.singleCellAnalysis(cell)

          # MULTI-CELL ANALYSIS
          self.multiCellAnalysis(cell)

     def initialize(self):
          # build initial outdated list
          for i in range(self.board.height):
               for j in range(self.board.width):
                    cell = self.board.grid[i][j]
                    if cell.isNumber and any(nb.isUnknown for nb in self.board.neighbors(cell)):
                         self.enqueue_outdated(cell)

     def run(self):
          # loops to analyse cells in the outdated pile and deletes them after the analysis until there are no outdated cells in the pile (no more changes have occurred)
          while self.outdated_q:
               # pick one cell, delete it & analyse it
               cell = self.dequeue_outdated()
               self.analyseCell(cell)
          print("Finished")

     # Output the board as viewed by the solver
     def print_solver_view(self):
          for y in range(self.board.height):
               row = []
               for x in range(self.board.width):
                    cell = self.board.grid[y][x]
                    if cell.isFlagged:
                         row.append('\033[31m*\033[0m')
                         self.num_bombs += 1
                    elif cell.revealed:
                         if cell.num == 0:
                              row.append(str(cell.num))
                         else:
                              row.append(f'\033[37;44m{str(cell.num)}\033[0m')
                    else:
                         row.append("?")
               print(" ".join(row))
          print()
          print(f"Number of BOMBS found: {self.num_bombs} out of {self.board.bomb_count}")
          print()

def debug_find_tier2_moves(solver):
     frontier = []
     for y in range(solver.board.height):
          for x in range(solver.board.width):
               A = solver.board.grid[y][x]
               if not A.isNumber:
                    continue
               _, nA, fA, UA, uA, bA = solver.cell_notation(A)
               if uA == 0:
                    continue
               frontier.append((A, UA, bA))

     found = 0
     for i in range(len(frontier)):
          A, UA, bA = frontier[i]
          for j in range(len(frontier)):
               if i == j:
                    continue
               B, UB, bB = frontier[j]

               # proper subset only (your code uses <)
               if not (UA < UB):
                    continue

               D = UB - UA
               k = bB - bA
               if k == 0 or k == len(D):
                    found += 1
                    print("ACTIONABLE Tier-2 pair:")
                    print(f" A=({A.x},{A.y}) bA={bA} |UA|={len(UA)}")
                    print(f" B=({B.x},{B.y}) bB={bB} |UB|={len(UB)}")
                    print(f" D size={len(D)} k={k} -> {'REVEAL D' if k==0 else 'FLAG D'}")
                    print(" D coords:", sorted([(c.x, c.y) for c in D]))
                    print()

     print(f"Total actionable Tier-2 moves available: {found}")

# ---- TEST SETUP ----

first_click = (2, 3)
board = Board(15, 15, 30, first_click)

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

print("DEBUG")
debug_find_tier2_moves(solver)