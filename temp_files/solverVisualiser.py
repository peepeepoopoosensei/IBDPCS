import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

from generator import Board
from solverTrace import TracedSolver


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
          self.setWindowTitle('MindSweeper Solver')

          # Load icon
          import os
          if os.path.exists('Icon.png'):
               self.setWindowIcon(QIcon('Icon.png'))

          # Parameters
          self.width = 10
          self.height = 10
          self.bomb_count = 15
          self.first_click = (5, 5)

          self.current_step = 0
          self.buttons = {}
          self.cell_pixmap = QPixmap('preview.png')

          self.setup_ui()  # creates step_label, buttons, etc.
          self.new_board()  # builds board+solver and calls display_step()

     def new_board(self):
          self.current_step = 0
          self.board = Board(self.width, self.height, self.bomb_count, self.first_click)
          self.solver = TracedSolver(self.board)
          # Run solver to collect all steps
          self.solver.initialize()
          self.solver.run()
          self.display_step()

     def setup_ui(self):

          # Central widget
          central_widget = QWidget()
          self.setCentralWidget(central_widget)

          # Main layout
          main_layout = QVBoxLayout()
          central_widget.setLayout(main_layout)

          title = QLabel("MindSweeper Solver")
          title.setAlignment(Qt.AlignmentFlag.AlignCenter)
          title.setStyleSheet("""
          QLabel {
               font-size: 26px;
               font-weight: 800;
               padding: 12px;
               color: #222;
          }
          """)

          subtitle = QLabel("Single-cell and multi-cell algorithm visualizer")
          subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
          subtitle.setStyleSheet("""
          QLabel {
               font-size: 13px;
               padding-bottom: 10px;
               color: #666;
          }
          """)

          main_layout.addWidget(title)
          main_layout.addWidget(subtitle)

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
                         scaled = self.cell_pixmap.scaled(40, 40, Qt.AspectRatioMode.IgnoreAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation)
                         btn.setIcon(QIcon(scaled))
                         btn.setIconSize(QSize(40, 40))

                    grid_layout.addWidget(btn, y, x)
                    self.buttons[(x, y)] = btn

          # Navigation controls
          nav_layout = QHBoxLayout()
          
          NAV_BTN = """
          QPushButton {
          background-color: #cfcfcf;
          border-top: 3px solid #ffffff;
          border-left: 3px solid #ffffff;
          border-right: 3px solid #7a7a7a;
          border-bottom: 3px solid #7a7a7a;
          padding: 8px 12px;
          font-size: 15px;
          font-weight: 700;
          }
          QPushButton:pressed {
          border-top: 3px solid #7a7a7a;
          border-left: 3px solid #7a7a7a;
          border-right: 3px solid #ffffff;
          border-bottom: 3px solid #ffffff;
          }
          QPushButton:disabled {
          color: #9a9a9a;
          }
          """

          self.prev_btn = QPushButton('← Previous')
          self.prev_btn.clicked.connect(self.prev_step)
          self.prev_btn.setStyleSheet(NAV_BTN)

          self.next_btn = QPushButton('Next →')
          self.next_btn.clicked.connect(self.next_step)
          self.next_btn.setStyleSheet(NAV_BTN)

          self.reset_btn = QPushButton('Reset')
          self.reset_btn.clicked.connect(self.reset_steps)
          self.reset_btn.setStyleSheet(NAV_BTN)

          self.new_btn = QPushButton('New Board')
          self.new_btn.clicked.connect(self.new_board)
          self.new_btn.setStyleSheet(NAV_BTN)

          nav_layout.addWidget(self.prev_btn)
          nav_layout.addWidget(self.reset_btn)
          nav_layout.addWidget(self.new_btn)
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
                         else:
                              btn.setText(str(num))
                              
                         colors = {
                         1: '#0000ff', 2: '#008000', 3: '#ff0000',
                         4: '#000080', 5: '#800000', 6: '#008080',
                         7: '#000000', 8: '#808080'
                         }
                         highlight_color = '#b0e0b0' if is_highlighted else '#d4d4d4'
                         border = '3px solid #00aa00' if is_highlighted else '1px solid #888'
                         btn.setStyleSheet(f"""
                         QPushButton {{
                         background-color: {highlight_color};
                         border: {border};
                         color: {colors.get(num, '#000000')};
                         font-size: 18px;
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


def main():
     app = QApplication(sys.argv)
     window = SolverVisualizerGUI()
     window.show()
     sys.exit(app.exec())

if __name__ == "__main__":
     main()