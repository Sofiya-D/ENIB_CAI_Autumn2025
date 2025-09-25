# coding: utf-8
DEBUG=True

import sys
# Check Python version for compatibility
major = sys.version_info.major
minor = sys.version_info.minor
if major < 3 or (major == 3 and minor < 6):
    # PyQt6 requires Python 3.6+
    if __name__ == "__main__":
        print(f"Your Python version is: {major}.{minor}")
        print("PyQt6 requires Python 3.6 or higher!")
        print("Please upgrade your Python version.")
    raise ImportError("PyQt6 requires Python 3.6+")
else:
    # Import PyQt6 modules
    from PyQt6.QtWidgets import QApplication
    if __name__ == "__main__":
        print(f"Your Python version is: {major}.{minor}")
        print("PyQt6 should work fine!")



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
        self.actions_binding()
        
    def show(self):
        self.view.show()
    
    def actions_binding(self) :
        if DEBUG :
            print(type(self).__name__+".actions_binding()")
        # self.scale_freq.bind("<B1-Motion>",self.on_frequency_action)
        # self.spinbox_samples.bind("<Button-1>",self.on_samples_action)
        self.view.folderselector.currentTextChanged.connect(self.folder_selection_changed)
        self.view.addfolderbutton.clicked.connect(self.add_folder)
        self.view.removefolderbutton.clicked.connect(self.remove_folder)


    def folder_selection_changed(self, new_folder_name):
        # TODO!(0)
        # If empty: disable 'Remove folder' button
        # Else: update paths & tree views --> handled in the view
        if DEBUG:
            print(f"Folder selection changed: {new_folder_name}")
        self.repo_model.set_selected_folder(new_folder_name=new_folder_name)


    def add_folder(self):
        # TODO!(0)
        if DEBUG:
            print(f"'Add folder' button clicked !")
        else:
            raise NotImplementedError


    def remove_folder(self):
        # TODO!(0)
        if DEBUG:
            print(f"'Remove folder' button clicked !")
        else:
            raise NotImplementedError



if __name__ == "__main__":
    print(">> Testing controllers.py <<")

    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    controller = MainController(db_filename="test", tablename="test")
    controller.show()  

    sys.exit(app.exec())