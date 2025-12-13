import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QLabel)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
import random
from collections import deque
import copy


class Cell:
    def __init__(self, board, x, y):
        self.board = board
        self.x = x
        self.y = y
        self.isBomb = False
        self.isFlagged = False
        self.revealed = False

    @property
    def num(self):
        if self.isBomb:
            return '*'
        return sum(1 for neighbor in self.board.neighbors(self) if neighbor.isBomb)
    
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


class SolverStep:
    """Represents one step in the solving process"""
    def __init__(self, board_state, action_type, cell=None, description=""):
        self.board_state = board_state  # snapshot of board
        self.action_type = action_type  # "flag", "reveal", "analyze"
        self.cell = cell  # which cell was affected
        self.description = description


class Solver:
    def __init__(self, board):
        self.num_bombs = 0
        self.board = board
        self.outdated = []
        self.steps = []  # Record all steps
        
    def record_step(self, action_type, cell=None, description=""):
        """Record current board state as a step"""
        board_snapshot = self.snapshot_board()
        step = SolverStep(board_snapshot, action_type, cell, description)
        self.steps.append(step)

    def snapshot_board(self):
        """Create a snapshot of current board state"""
        snapshot = []
        for y in range(self.board.height):
            row = []
            for x in range(self.board.width):
                cell = self.board.grid[y][x]
                row.append({
                    'revealed': cell.revealed,
                    'isFlagged': cell.isFlagged,
                    'isBomb': cell.isBomb,
                    'num': cell.num
                })
            snapshot.append(row)
        return snapshot

    def initialize(self):
        self.record_step("init", description="Initial board state")
        
        for i in range(self.board.height):
            for j in range(self.board.width):
                cell = self.board.grid[i][j]
                if cell not in self.outdated and cell.revealed and not cell.isBomb and any((not x.revealed and not x.isFlagged)for x in self.board.neighbors(cell)):
                    self.outdated.append(cell)
        
        self.record_step("init", description=f"Found {len(self.outdated)} cells to analyze")

    def run(self):
        while self.outdated:
            cell = self.outdated.pop(0)
            self.analyseCell(cell)
        
        self.record_step("complete", description="Solving complete!")

    def analyseCell(self, cell):
        self.record_step("analyze", cell, f"Analyzing cell at ({cell.x}, {cell.y})")
        
        neighbors = list(self.board.neighbors(cell))
        n = cell.num
        f = sum(1 for x in neighbors if x.isFlagged)
        u = sum(1 for x in neighbors if not x.revealed and not x.isFlagged)
        
        if n - f < 0 or n - f > u:
            self.record_step("error", cell, "Error detected!")
        elif n - f == u:
            # Flag all unknowns
            for i in range(len(neighbors)):
                if neighbors[i].isUnknown:
                    changed_cell = neighbors[i]
                    changed_cell.isFlagged = True
                    self.record_step("flag", changed_cell, f"Flagged bomb at ({changed_cell.x}, {changed_cell.y})")
                    
                    adjacents = list(self.board.neighbors(changed_cell))
                    for j in range(len(adjacents)):
                        if adjacents[j].isNumber and adjacents[j] not in self.outdated:
                            self.outdated.append(adjacents[j])
        elif n == f:
            # Reveal all unknowns
            for i in range(len(neighbors)):
                if neighbors[i].isUnknown:
                    changed_cell = neighbors[i]
                    changed_cell.revealed = True
                    self.record_step("reveal", changed_cell, f"Revealed safe cell at ({changed_cell.x}, {changed_cell.y})")
                    
                    adjacents = list(self.board.neighbors(changed_cell))
                    for j in range(len(adjacents)):
                        if adjacents[j].isNumber and adjacents[j] not in self.outdated:
                            self.outdated.append(adjacents[j])


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
        
        # Create board and solver
        self.width = 10
        self.height = 10
        self.bomb_count = 10
        first_click = (5, 5)
        
        self.board = Board(self.width, self.height, self.bomb_count, first_click)
        self.solver = Solver(self.board)
        
        # Run solver to collect all steps
        self.solver.initialize()
        self.solver.run()
        
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
                is_highlighted = step.cell and step.cell.x == x and step.cell.y == y
                
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
