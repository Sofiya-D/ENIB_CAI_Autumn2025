from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
import sys

from controllers import MainController


app = QApplication(sys.argv)

controller = MainController()
controller.show()  

sys.exit(app.exec())

