import sys

def main():
     mode = "viz"
     if len(sys.argv) >= 2:
          mode = sys.argv[1].lower().strip()

     if mode in ("play", "game"):
          import gameGUI
          gameGUI.main()
     else:
          import solverVisualiser
          solverVisualiser.main()

if __name__ == "__main__":
     main()