from models import RepoModel
from views import MainWindow

class MainController:
    def __init__(self, 
                 db_filename = "Folder_Data.db", 
                 tablename = "tracked_folders"):
        
        self.repo_model = RepoModel(db_filename=db_filename, 
                                    tablename=tablename)
        self.view = MainWindow()
        self.repo_model.attach(self.view)
        self.repo_model.initialize_folders_db()
        
    def show(self):
        self.view.show()


if __name__ == "__main__":
    print(">> Testing controllers.py <<")

    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    controller = MainController(db_filename="test", tablename="test")
    controller.show()  

    sys.exit(app.exec())