# coding: utf-8
DEBUG=True

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

class MainController:
    def __init__(self, 
                 repo_model,
                 view):
        
        self.repo_model = repo_model
        self.view = view
        self.actions_binding()
        
    def show(self):
        self.view.show()
    
    def actions_binding(self) :
        if DEBUG :
            print(type(self).__name__+".actions_binding()")
        self.view.folderselector.currentTextChanged.connect(self.folder_selection_changed)
        self.view.addfolderbutton.clicked.connect(self.add_folder)
        self.view.removefolderbutton.clicked.connect(self.remove_folder)
        self.view.changenamebutton.clicked.connect(self.change_foldername)
        self.view.changepathbutton.clicked.connect(self.change_paths)
        self.view.add_action.triggered.connect(self.add_folder)
        self.view.remove_action.triggered.connect(self.remove_folder)
        self.view.edit_action.triggered.connect(self.remove_folder)



    def folder_selection_changed(self, new_folder_name):
        if DEBUG:
            print(f"Folder selection changed: {new_folder_name}")
        self.repo_model.set_selected_folder(new_folder_name=new_folder_name)


    def add_folder(self):
        if DEBUG:
            print(type(self).__name__+".add_folder()")
        foldername, local_path, remote_path = self.view.prompt_add_folder()
        if foldername and local_path and remote_path :
            self.repo_model.add_new_folder_to_db(foldername=foldername, 
                                                 local_path=local_path, 
                                                 remote_path=remote_path)


    def remove_folder(self):
        if DEBUG:
            print(type(self).__name__+".remove_folder()")
        confirmation = self.view.prompt_confirmation("delete a folder")
        if confirmation:
            if DEBUG:
                print("Deletion confirmed.")
            delete_tracking_files = True
            self.repo_model.remove_folder_from_db(self.repo_model.get_selected_folder(), delete_tracking_files=delete_tracking_files)
        else:
            if DEBUG:
                print("Deletion cancelled.")


    def change_foldername(self):
        # TODO!(0)
        if DEBUG:
            print(type(self).__name__+".change_foldername()")
        current_folder = self.repo_model.get_selected_folder()
        new_foldername = self.view.prompt_new_foldername()
        self.repo_model.set_folder_data(current_folder,
                                        new_name=new_foldername)


    def change_paths(self):
        # TODO!(0)
        if DEBUG:
            print(type(self).__name__+".change_paths()")
        else:
            raise NotImplementedError



if __name__ == "__main__":
    print(">> Testing controllers.py <<")

    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    repo_model = RepoModel("test", "test")
    view = MainWindow()
    repo_model.attach(view)
    repo_model.initialize_folders_db()
    controller = MainController(repo_model=repo_model, view=view)
    controller.show()  

    sys.exit(app.exec())