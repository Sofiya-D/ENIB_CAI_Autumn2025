# coding: utf-8
DEBUG=False


import sys
# Check Python version for compatibility
major = sys.version_info.major
minor = sys.version_info.minor
if major < 3 or (major == 3 and minor < 6):
    # PyQt5 requires Python 3.6+
    if __name__ == "__main__":
        print(f"Your Python version is: {major}.{minor}")
        print("PyQt5 requires Python 3.6 or higher!")
        print("Please upgrade your Python version.")
    raise ImportError("PyQt5 requires Python 3.6+")
else:
    # Import PyQt5 modules
    from PyQt5.QtWidgets import QApplication
    if __name__ == "__main__":
        print(f"Your Python version is: {major}.{minor}")
        print("PyQt5 should work fine!")


from models import RepoModel
from views import MainWindow
from controllers import MainController

class MainApp(QApplication):
    def __init__(self, args=None):
        super().__init__(args)
        self.menubar()
        self.create()

    def create(self) :
        self.model=RepoModel() 
        self.view=MainWindow() # init window

        self.control=MainController(self.model,self.view)
        self.model.attach(self.view)

        self.view.show()

    def menubar(self) :
        pass


if __name__=="__main__" :

    app = MainApp(sys.argv)
    

    sys.exit(app.exec())

