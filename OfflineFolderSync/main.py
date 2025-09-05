import sys
from PyQt5.QtWidgets import QApplication

from models import RepoModel
from views import MainWindow
from controllers import MainController


def main():
    app = QApplication(sys.argv)

    # Modèle
    model = RepoModel()

    # Vue
    view = MainWindow()

    # Contrôleur
    controller = MainController(model, view)

    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
