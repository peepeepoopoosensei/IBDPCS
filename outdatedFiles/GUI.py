import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sweeper of the mind')
        self.setWindowIcon(QIcon('Icon.png'))
        self.resize(400,400) # width , height

        layout = QVBoxLayout() # organize widgets
        self.setLayout(layout)
        # sets layout as itself

        #Widgets instances
        button = QPushButton('Hello',clicked=self.sayHello)
        # button pusher
        self.inputField = QLineEdit()
        # line in which
        self.output = QTextEdit()
        # output field


        # add widgets to window
        layout.addWidget(self.inputField)
        layout.addWidget(button)
        layout.addWidget(self.output)

    # create function to say hello to output field
    def sayHello (self,):
        input = self.inputField.text()
        self.output.setText('Hi {0}'.format(input))



app = QApplication([])

# sets style sheet (fonts etc)
app.setStyleSheet('''
        QWidget {font-size : 25px ;}   
''')

window = MyApp()
window.show()
sys.exit(app.exec())
# makes it so the app execution after it is closed closes the process as well

