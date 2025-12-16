import sys

if __name__ == "__main__":
     mode = "viz"
     if len(sys.argv) >= 2:
          mode = sys.argv[1].lower()

     if mode == "play":
          import gameGUI
          gameGUI.main()
     else:
          import solverVisualiser
          solverVisualiser.main()