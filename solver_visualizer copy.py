import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
import random
from collections import deque
import copy
from  Generator import Board, Cell
from solver import Solver

class Board:
    def __init__(self, width, height, bomb_count, first_selection):
        self.width = width
        self.height = height
        self.bomb_count = bomb_count
        self.first_selection = first_selection
        self.grid = [
            [Cell(self, x, y) for x in range(width)]
            for y in range(height)
        ]
        self.place_bombs(first_selection)
        self._initial_zero_expand()

    def neighbors(self, cell):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cell.x + dx, cell.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    yield self.grid[ny][nx]

    def place_bombs(self, first_selection):
        fx, fy = first_selection
        candidates = []

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) == (fx, fy) or (abs(x - fx) <= 1 and abs(y - fy) <= 1):
                    self.grid[y][x].revealed = True
                    continue
                candidates.append((x, y))

        bomb_positions = random.sample(candidates, self.bomb_count)
        for (x, y) in bomb_positions:
            self.grid[y][x].isBomb = True

    def _initial_zero_expand(self):
        q = deque()
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

            for n in self.neighbors(cur):
                if not n.isBomb and not n.revealed:
                    n.revealed = True
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


class SolverStep:
    """Represents one step in the solving process"""
    def __init__(self, board_state, action_type, cell_xy=None, description=""):
        self.board_state = board_state  # snapshot of board
        self.action_type = action_type  # "flag", "reveal", "analyze"
        self.cell_xy = cell_xy  # which cell was affected
        self.description = description


class Solver:
    def __init__(self, board):
        self.board = board
        # step recording
        self.steps = []
        self.num_bombs = 0
        # collection of outdated numbered cells
        self.outdated_q = deque()  # queue of cells to process
        self.outdated_set = set()  # membership check (no duplicates)
        
    def record_step(self, action_type, cell=None, description=""):
        """Record current board state as a step"""
        board_snapshot = self.snapshot_board()
        xy = (cell.x, cell.y) if cell else None
        step = SolverStep(board_snapshot, action_type, xy, description)
        self.steps.append(step)

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
                    'isBomb': cell.isBomb,
                    'num': num
                })
            snapshot.append(row)
        return snapshot

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
        # record flag step
        self.record_step("flag", c, f"Flagged ({c.x},{c.y})")

        # adds affected adjacent numbered cells to the outdated pile
        adjacents = self.board.neighbors(c)
        for adj in adjacents:
            if adj.isNumber:
                self.enqueue_outdated(adj)

    # reveal a cell and add affected num. cells to the outdated pile
    def revealCell(self, c):
        assert c.isUnknown  # catches mistakes during development
        c.revealed = True
        # record reveal step
        self.record_step("reveal", c, f"Revealed ({c.x},{c.y})")

        # enqueue the revealed cell itself
        if c.isNumber and any(nb.isUnknown for nb in self.board.neighbors(c)):
            self.enqueue_outdated(c)
        # adds affected neighbouring numbered cells to the outdated pile
        adjacents = self.board.neighbors(c)
        for adj in adjacents:
            if adj.isNumber:
                self.enqueue_outdated(adj)

    def singleCellAnalysis(self, cell):
        # record single-cell analysis step
        self.record_step("analyze", cell, f"Analyzing cell at ({cell.x}, {cell.y})")

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
        # record multi-cell analysis step
        self.record_step("analyze", cell, f"Analyzing cell at ({cell.x}, {cell.y})")

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
        self.record_step("init", description="Initial board state")

        # build initial outdated list
        for i in range(self.board.height):
            for j in range(self.board.width):
                cell = self.board.grid[i][j]
                if cell.isNumber and any(nb.isUnknown for nb in self.board.neighbors(cell)):
                        self.enqueue_outdated(cell)
        
        self.record_step("init", description=f"Found {len(self.outdated_q)} cells to analyze")

    def run(self):
        # loops to analyse cells in the outdated pile and deletes them after the analysis until there are no outdated cells in the pile (no more changes have occurred)
        while self.outdated_q:
            # pick one cell, delete it & analyse it
            cell = self.dequeue_outdated()
            self.analyseCell(cell)
        print("Finished")

        self.record_step("complete", description="Solving complete!")
    

    # Helper functions for debugging

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

class CellButton(QPushButton):
    def __init__(self, x, y, parent=None):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.setFixedSize(40, 40)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                font-size: 16px;
                font-weight: bold;
            }
        """)


class SolverVisualizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Minesweeper Solver - Step by Step')

        # Load icon
        import os
        if os.path.exists('Icon.png'):
            self.setWindowIcon(QIcon('Icon.png'))
        
        # Create board and solver (parameters)
        self.width = 10
        self.height = 10
        self.bomb_count = 20
        first_click = (5, 5)
        
        self.board = Board(self.width, self.height, self.bomb_count, first_click)
        self.solver = Solver(self.board)
        
        # DEBUG prints
        print("REAL BOARD (with bombs hidden):")
        self.board.print_board(show_bombs=False)
        print("REAL BOARD (with bombs visible - DEBUG):")
        self.board.print_board(show_bombs=True)
        solver = Solver(self.board)
        print("INITIAL SOLVER VIEW:")
        solver.print_solver_view()

        # Run solver to collect all steps
        self.solver.initialize()
        self.solver.run()

        # DEBUG prints 2.0
        print("FINAL SOLVER VIEW:")
        solver.print_solver_view()
        print("FINAL REAL BOARD (DEBUG):")
        self.board.print_board(show_bombs=True)

        self.current_step = 0
        self.buttons = {}
        
        # Load cell image
        self.cell_pixmap = QPixmap('preview.png')
        
        self.setup_ui()
        self.display_step()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Step info label
        self.step_label = QLabel()
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setStyleSheet("font-size: 14px; padding: 10px; font-weight: bold;")
        main_layout.addWidget(self.step_label)
        
        # Description label
        self.desc_label = QLabel()
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setStyleSheet("font-size: 12px; padding: 5px;")
        self.desc_label.setWordWrap(True)
        main_layout.addWidget(self.desc_label)
        
        # Grid layout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        grid_container = QWidget()
        grid_container.setLayout(grid_layout)
        main_layout.addWidget(grid_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Create grid buttons
        for y in range(self.height):
            for x in range(self.width):
                btn = CellButton(x, y)
                btn.setEnabled(False)  # Not clickable in visualizer
                
                if not self.cell_pixmap.isNull():
                    scaled_pixmap = self.cell_pixmap.scaled(40, 40, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    btn.setIcon(QIcon(scaled_pixmap))
                    btn.setIconSize(QSize(40, 40))
                
                grid_layout.addWidget(btn, y, x)
                self.buttons[(x, y)] = btn
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton('← Previous')
        self.prev_btn.clicked.connect(self.prev_step)
        self.prev_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        
        self.next_btn = QPushButton('Next →')
        self.next_btn.clicked.connect(self.next_step)
        self.next_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        
        self.reset_btn = QPushButton('Reset')
        self.reset_btn.clicked.connect(self.reset_steps)
        self.reset_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.reset_btn)
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)
        
    def display_step(self):
        """Display the current step"""
        if self.current_step >= len(self.solver.steps):
            self.current_step = len(self.solver.steps) - 1
        if self.current_step < 0:
            self.current_step = 0
            
        step = self.solver.steps[self.current_step]
        
        # Update labels
        self.step_label.setText(f"Step {self.current_step + 1} / {len(self.solver.steps)}")
        self.desc_label.setText(step.description)
        
        # Update board display
        for y in range(self.height):
            for x in range(self.width):
                cell_state = step.board_state[y][x]
                btn = self.buttons[(x, y)]
                
                # Check if this is the highlighted cell
                is_highlighted = (step.cell_xy == (x, y))
                
                if cell_state['isFlagged']:
                    btn.setIcon(QIcon())
                    btn.setText('🚩')
                    highlight_color = '#ffaa00' if is_highlighted else '#ffcc00'
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {highlight_color};
                            border: 2px solid #ff8800;
                            font-size: 16px;
                            padding: 0px;
                            margin: 0px;
                        }}
                    """)
                elif cell_state['revealed']:
                    btn.setIcon(QIcon())
                    num = cell_state['num']
                    
                    if num == 0:
                        btn.setText('')
                        highlight_color = '#b0e0b0' if is_highlighted else '#d4d4d4'
                    else:
                        btn.setText(str(num))
                        highlight_color = '#b0e0b0' if is_highlighted else '#d4d4d4'
                    
                    colors = {
                        1: '#0000ff', 2: '#008000', 3: '#ff0000',
                        4: '#000080', 5: '#800000', 6: '#008080',
                        7: '#000000', 8: '#808080'
                    }
                    
                    border = '3px solid #00aa00' if is_highlighted else '1px solid #888'
                    
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {highlight_color};
                            border: {border};
                            color: {colors.get(num, '#000000')};
                            font-size: 16px;
                            font-weight: bold;
                            padding: 0px;
                            margin: 0px;
                        }}
                    """)
                else:
                    # Unknown cell
                    btn.setText('')
                    if not self.cell_pixmap.isNull():
                        scaled_pixmap = self.cell_pixmap.scaled(40, 40, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        btn.setIcon(QIcon(scaled_pixmap))
                        btn.setIconSize(QSize(40, 40))
                    
                    border = '3px solid #00aa00' if is_highlighted else 'none'
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: transparent;
                            border: {border};
                            padding: 0px;
                            margin: 0px;
                        }}
                    """)
        
        # Update button states
        self.prev_btn.setEnabled(self.current_step > 0)
        self.next_btn.setEnabled(self.current_step < len(self.solver.steps) - 1)
        
    def next_step(self):
        if self.current_step < len(self.solver.steps) - 1:
            self.current_step += 1
            self.display_step()
            
    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.display_step()
            
    def reset_steps(self):
        self.current_step = 0
        self.display_step()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SolverVisualizerGUI()
    window.show()
    sys.exit(app.exec())
    