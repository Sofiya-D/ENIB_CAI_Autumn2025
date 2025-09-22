import sys
from PyQt5.QtWidgets import QApplication

from models import RepoModel
from views import MainWindow
from controllers import MainController


def main():
    app = QApplication(sys.argv)
    model = RepoModel()
    view = MainWindow()
    controller = MainController(model, view)
    
    def cleanup():
        model.close()

    app.aboutToQuit.connect(cleanup)
    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()