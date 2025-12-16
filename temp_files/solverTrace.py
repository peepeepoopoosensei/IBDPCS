import copy
from solverCore import Solver


class SolverStep:
     """Represents one step in the solving process"""
     def __init__(self, board_state, action_type, cell_xy=None, description=""):
          self.board_state = board_state  # snapshot of board
          self.action_type = action_type  # "flag", "reveal", "analyze", "init", "complete"
          self.cell_xy = cell_xy          # (x, y) tuple (IMPORTANT: not a Cell object)
          self.description = description


class TracedSolver(Solver):
     def __init__(self, board):
          super().__init__(board)
          self.steps = []  # Record all steps

     def snapshot_board(self):
          """Create a snapshot of current board state"""
          snapshot = []
          for y in range(self.board.height):
               row = []
               for x in range(self.board.width):
                    cell = self.board.grid[y][x]

                    num = cell.num
                    # Normalize: bombs store num=None instead of "*"
                    if num == '*':
                         num = None

                    row.append({
                         'revealed': cell.revealed,
                         'isFlagged': cell.isFlagged,
                         'isBomb': cell.isBomb,   # keep if you want debug/optional reveal
                         'num': cell.num          # keep as-is (GUI must handle '*' if it ever appears)
                    })
               snapshot.append(row)
          return snapshot

     def record_step(self, action_type, cell_xy=None, description=""):
          board_snapshot = self.snapshot_board()
          step = SolverStep(board_snapshot, action_type, cell_xy, description)
          self.steps.append(step)

     # ---- override "actions" to add recording, algorithm unchanged (super() does real work)

     def flagCell(self, c):
          super().flagCell(c)
          self.record_step("flag", (c.x, c.y), f"Flagged cell at ({c.x}, {c.y})")

     def revealCell(self, c):
          super().revealCell(c)
          self.record_step("reveal", (c.x, c.y), f"Revealed cell at ({c.x}, {c.y})")

     def analyseCell(self, cell):
          self.record_step("analyze", (cell.x, cell.y), f"Analyzing cell at ({cell.x}, {cell.y})")
          super().analyseCell(cell)

     def initialize(self):
          self.record_step("init", description="Initial board state")
          super().initialize()
          self.record_step("init", description=f"Found {len(self.outdated_q)} cells to analyze")

     def run(self):
          super().run()
          self.record_step("complete", description="Solving complete!")