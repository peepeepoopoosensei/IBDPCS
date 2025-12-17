import sys
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class Launcher(QWidget):
     def __init__(self):
          super().__init__()
          self.setWindowTitle("MindSweeper Launcher")
          self.setFixedSize(360, 260)

          layout = QVBoxLayout(self)

          layout.setContentsMargins(20, 20, 20, 30)  # extra bottom margin
          layout.setSpacing(12)

          title = QLabel("MindSweeper")
          title.setAlignment(Qt.AlignmentFlag.AlignCenter)
          title.setStyleSheet("font-size: 24px; font-weight: 800; padding: 10px;")
          layout.addWidget(title)

          subtitle = QLabel("Choose a mode:")
          subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
          subtitle.setStyleSheet("font-size: 13px; color: #666; padding-bottom: 10px;")
          layout.addWidget(subtitle)

          play_btn = QPushButton("Play Game")
          viz_btn = QPushButton("Solver Visualiser")

          btn_style = """
          QPushButton {
               background-color: #cfcfcf;
               border-top: 3px solid #ffffff;
               border-left: 3px solid #ffffff;
               border-right: 3px solid #7a7a7a;
               border-bottom: 3px solid #7a7a7a;
               padding: 10px 12px;
               font-size: 15px;
               font-weight: 700;
          }
          QPushButton:pressed {
               border-top: 3px solid #7a7a7a;
               border-left: 3px solid #7a7a7a;
               border-right: 3px solid #ffffff;
               border-bottom: 3px solid #ffffff;
          }
          """
          play_btn.setStyleSheet(btn_style)
          viz_btn.setStyleSheet(btn_style)

          play_btn.clicked.connect(lambda: self.launch("play"))
          viz_btn.clicked.connect(lambda: self.launch("viz"))

          layout.addWidget(play_btn)
          layout.addWidget(viz_btn)

     def launch(self, mode: str):
          repo_dir = Path(__file__).resolve().parent
          main_py = repo_dir / "main.py"

          # Launch as a new process so we don't fight over QApplication
          subprocess.Popen([sys.executable, str(main_py), mode], cwd=str(repo_dir))

          # Close the launcher
          QApplication.quit()


def main():
     app = QApplication(sys.argv)
     w = Launcher()
     w.show()
     sys.exit(app.exec())


if __name__ == "__main__":
     main()