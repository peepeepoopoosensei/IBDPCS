import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QPushButton, QLabel)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize, pyqtSignal
import random
from pathlib import Path
from collections import deque
from generator import Board


class CellButton(QPushButton):
     rightClicked = pyqtSignal(int, int)

     def __init__(self, x, y, parent=None):
          super().__init__(parent)
          self.x = x
          self.y = y
          self.setFixedSize(50, 50)
          self.setContentsMargins(0, 0, 0, 0)
          self.setStyleSheet("""
               QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 0px;
                    margin: 0px;
                    font-size: 20px;
                    font-weight: bold;
               }
          """)
     
     def mousePressEvent(self, event):
          if event.button() == Qt.MouseButton.RightButton:
               self.rightClicked.emit(self.x, self.y)
               event.accept()
               return
          super().mousePressEvent(event)


class MinesweeperGUI(QMainWindow):
     def __init__(self):
          super().__init__()
          self.setWindowTitle('MindSweeper Game')

          # Load icon
          ASSETS_DIR = Path(__file__).resolve().parent
          icon_path = ASSETS_DIR / "Icon.png"
          if icon_path.exists():
               self.setWindowIcon(QIcon(str(icon_path)))

          # Game parameters
          self.width = 10
          self.height = 10
          self.bomb_count = 15
          self.board = None
          self.buttons = {}
          self.first_click = True

          # Load cell image
          self.cell_pixmap = QPixmap(str(ASSETS_DIR / "preview.png"))
          if self.cell_pixmap.isNull():
               print("Warning: preview.png not found!")

          # Setup UI
          self.setup_ui()

     def setup_ui(self):

          # Central widget
          central_widget = QWidget()
          self.setCentralWidget(central_widget)

          # Main layout
          main_layout = QVBoxLayout()
          central_widget.setLayout(main_layout)

          title = QLabel("MindSweeper Game")
          title.setAlignment(Qt.AlignmentFlag.AlignCenter)
          title.setStyleSheet("""
          QLabel {
               font-size: 26px;
               font-weight: 800;
               padding: 12px;
               color: #222;
          }
          """)

          subtitle = QLabel("Play the infamous Minesweeper game! (under the new name MindSweeper)")
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

          # Info label
          self.info_label = QLabel('Click any cell to start!')
          self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
          self.info_label.setStyleSheet("font-size: 16px; padding: 10px;")
          main_layout.addWidget(self.info_label)

          # Grid layout for the board
          grid_layout = QGridLayout()
          grid_layout.setSpacing(0)  # No spacing between cells
          grid_layout.setContentsMargins(0, 0, 0, 0)  # No margins around the grid

          # Create a container widget for the grid to control its size
          grid_container = QWidget()
          grid_container.setLayout(grid_layout)
          main_layout.addWidget(grid_container, alignment=Qt.AlignmentFlag.AlignCenter)

          # Create buttons for each cell
          for y in range(self.height):
               for x in range(self.width):
                    btn = CellButton(x, y)
                    btn.clicked.connect(lambda checked, bx=x, by=y: self.on_cell_click(bx, by))
                    btn.rightClicked.connect(self.on_cell_right_click)

                    # Set the image as icon - scaled to button size
                    if not self.cell_pixmap.isNull():
                         scaled_pixmap = self.cell_pixmap.scaled(50, 50, Qt.AspectRatioMode.IgnoreAspectRatio,
                                                                 Qt.TransformationMode.SmoothTransformation)
                         btn.setIcon(QIcon(scaled_pixmap))
                         btn.setIconSize(QSize(50, 50))

                    grid_layout.addWidget(btn, y, x)
                    self.buttons[(x, y)] = btn

          # Reset button
          RESET_BTN = """
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
          reset_btn = QPushButton('New Game')
          reset_btn.clicked.connect(self.reset_game)
          reset_btn.setStyleSheet(RESET_BTN)
          main_layout.addWidget(reset_btn)

     def on_cell_click(self, x, y):
          # First click - create board
          if self.first_click:
               self.board = Board(self.width, self.height, self.bomb_count, (x, y))
               self.first_click = False
               self.update_display()
               self.info_label.setText(f'Bombs: {self.bomb_count}')
               return

          # Get the cell
          cell = self.board.grid[y][x]

          if cell.isFlagged:
               return

          # If already revealed, ignore
          if cell.revealed:
               return

          # Reveal the cell
          cell.revealed = True

          # Check if bomb
          if cell.isBomb:
               self.game_over(False)
               return

          # If zero, expand
          if cell.num == 0:
               self.expand_zeros(cell)

          # Update display
          self.update_display()

          # Check for win
          self.check_win()
     
     def on_cell_right_click(self, x, y):
          if self.first_click or self.board is None:
               return

          cell = self.board.grid[y][x]
          if cell.revealed:
               return

          cell.isFlagged = not cell.isFlagged
          self.update_display()

     def expand_zeros(self, cell):
          q = deque([cell])
          seen = set()

          while q:
               cur = q.popleft()
               if cur in seen:
                    continue
               seen.add(cur)

               for n in self.board.neighbors(cur):
                    if not n.isBomb and not n.revealed:
                         n.revealed = True
                         if n.num == 0 and n not in seen:
                              q.append(n)

     def update_display(self):
          for y in range(self.height):
               for x in range(self.width):
                    cell = self.board.grid[y][x]
                    btn = self.buttons[(x, y)]

                    if cell.revealed:
                         btn.setIcon(QIcon())  # Remove the cell image
                         btn.setStyleSheet("""
                         QPushButton {
                              background-color: #d4d4d4;
                              border: 1px solid #888;
                              font-size: 20px;
                              font-weight: bold;
                         }
                         """)

                         if cell.isBomb:
                              # Load and show mine icon
                              import os
                              mine_pixmap = QPixmap('Icon.png')

                              if not mine_pixmap.isNull():
                                   scaled_mine = mine_pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                                                      Qt.TransformationMode.SmoothTransformation)
                                   btn.setIcon(QIcon(scaled_mine))
                                   btn.setIconSize(QSize(40, 40))
                              btn.setStyleSheet("""
                                   QPushButton {
                                        background-color: #ff4444;
                                        border: 1px solid #888;
                                   }
                              """)
                         else:
                              num = cell.num
                              if num == 0:
                                   btn.setText('')
                              else:
                                   btn.setText(str(num))
                                   colors = {
                                        1: '#0000ff', 2: '#008000', 3: '#ff0000',
                                        4: '#000080', 5: '#800000', 6: '#008080',
                                        7: '#000000', 8: '#808080'
                                   }
                                   btn.setStyleSheet(f"""
                                        QPushButton {{
                                             background-color: #d4d4d4;
                                             border: 1px solid #888;
                                             color: {colors.get(num, '#000000')};
                                             font-size: 23px;
                                             font-weight: bold;
                                        }}
                                   """)
                         btn.setEnabled(False)
                    else:  # NOT revealed: either flagged or covered
                         btn.setEnabled(True)
                         if cell.isFlagged:
                              btn.setIcon(QIcon())
                              btn.setText("🚩")
                              btn.setStyleSheet("""
                              QPushButton {
                                   background-color: '#ffcc00';
                                   border: 2px solid #ff8800;
                                   font-size: 20px;
                                   font-weight: bold;
                              }
                              """)
                         else:
                              btn.setText("")
                              btn.setStyleSheet("""
                              QPushButton {
                                   background-color: transparent;
                                   border: none;
                                   font-size: 20px;
                                   font-weight: bold;
                              }
                              """)
                              if not self.cell_pixmap.isNull():
                                   scaled = self.cell_pixmap.scaled(
                                        50, 50,
                                        Qt.AspectRatioMode.IgnoreAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation
                                   )
                                   btn.setIcon(QIcon(scaled))
                                   btn.setIconSize(QSize(50, 50))

     def check_win(self):
          # Check if all non-bomb cells are revealed
          for y in range(self.height):
               for x in range(self.width):
                    cell = self.board.grid[y][x]
                    if not cell.isBomb and not cell.revealed:
                         return
          self.game_over(True)

     def game_over(self, won):
          # Reveal all cells
          for y in range(self.height):
               for x in range(self.width):
                    self.board.grid[y][x].revealed = True

          self.update_display()
          if won:
               self.info_label.setText('🎉 You Won! 🎉')
          else:
               self.info_label.setText('💥 Game Over! 💥')

     def reset_game(self):
          self.first_click = True
          self.board = None

          # Reset all buttons
          for y in range(self.height):
               for x in range(self.width):
                    btn = self.buttons[(x, y)]
                    btn.setText('')
                    btn.setEnabled(True)
                    btn.setStyleSheet("""
                         QPushButton {
                         background-color: transparent;
                         border: none;
                         font-size: 20px;
                         font-weight: bold;
                         }
                    """)
                    if not self.cell_pixmap.isNull():
                         scaled_pixmap = self.cell_pixmap.scaled(50, 50, Qt.AspectRatioMode.IgnoreAspectRatio,
                                                                 Qt.TransformationMode.SmoothTransformation)
                         btn.setIcon(QIcon(scaled_pixmap))
                         btn.setIconSize(QSize(50, 50))

          self.info_label.setText('Click any cell to start!')


def main():
     app = QApplication(sys.argv)
     window = MinesweeperGUI()
     window.show()
     sys.exit(app.exec())

if __name__ == "__main__":
     main()