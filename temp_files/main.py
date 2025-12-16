import sys
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


HERE = Path(__file__).resolve().parent
PY = sys.executable


class ModePicker(QWidget):
     def __init__(self):
          super().__init__()
          self.setWindowTitle("MindSweeper Launcher")
          self.setFixedSize(360, 220)

          layout = QVBoxLayout()
          layout.setSpacing(12)
          self.setLayout(layout)

          title = QLabel("MindSweeper")
          title.setAlignment(Qt.AlignmentFlag.AlignCenter)
          title.setStyleSheet("font-size: 22px; font-weight: 800; padding-top: 10px;")

          subtitle = QLabel("Choose between:")
          subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
          subtitle.setStyleSheet("font-size: 12px; color: #666; padding-bottom: 6px;")

          btn_viz = QPushButton("Solver Visualiser")
          btn_play = QPushButton("Play Game")

          # optional nicer button styling
          btn_style = """
          QPushButton {
               background-color: #cfcfcf;
               border-top: 3px solid #ffffff;
               border-left: 3px solid #ffffff;
               border-right: 3px solid #7a7a7a;
               border-bottom: 3px solid #7a7a7a;
               padding: 10px 12px;
               font-size: 14px;
               font-weight: 700;
          }
          QPushButton:pressed {
               border-top: 3px solid #7a7a7a;
               border-left: 3px solid #7a7a7a;
               border-right: 3px solid #ffffff;
               border-bottom: 3px solid #ffffff;
          }
          """
          btn_viz.setStyleSheet(btn_style)
          btn_play.setStyleSheet(btn_style)

          btn_viz.clicked.connect(self.launch_viz)
          btn_play.clicked.connect(self.launch_play)

          layout.addWidget(title)
          layout.addWidget(subtitle)
          layout.addWidget(btn_viz)
          layout.addWidget(btn_play)

     def _spawn(self, filename: str):
          target = HERE / filename
          subprocess.Popen([PY, str(target)], cwd=str(HERE))
          QApplication.quit()

     def launch_viz(self):
          self._spawn("solverVisualiser.py")

     def launch_play(self):
          self._spawn("gameGUI.py")


def main():
     app = QApplication(sys.argv)
     w = ModePicker()
     w.show()
     sys.exit(app.exec())


if __name__ == "__main__":
     main()