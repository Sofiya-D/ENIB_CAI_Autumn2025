# controllers.py
# Handles the logic between model and view
# ie, communication and data flow
# Where the main application logic lives

from ast import main
import os
from PyQt5.QtWidgets import QMessageBox, QApplication
import io, sys

from models import RepoModel
from views import MainWindow

class MainController:

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.controller = self  # Link view back to controller

        # Connect view buttons to controller methods
        self.view.set_add_folder_callback(self.add_folder_dialog)
        self.view.set_change_paths_callback(self.change_folder_paths_dialog)
        self.view.set_remove_folder_callback(self.remove_folder_dialog)

        # Initialisation
        self.refresh_view()


    def add_folder_dialog(self):
        result = self.view.prompt_add_folder()
        if not result:
            return
        foldername, local_path, usb_path = result
        # Use 'modified' as initial status, and empty hash
        # Try to add folder, but capture error output
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        try:
            self.model.add_folder_to_db(foldername, 'modified', local_path, usb_path) # foldername, status, local_hash, usb_hash, local_path, usb_path
        except Exception as e:
            print(f"Error adding folder '{foldername}': {e}")
            self.view.new_log(f"Error adding folder '{foldername}': {e}")
        sys.stdout = old_stdout
        output = mystdout.getvalue()
        if "Folder not added." in output:
            QMessageBox.warning(self.view, "Add Folder Failed", output)
            self.view.new_log(output.strip())
        else:
            self.view.new_log(f"Added folder '{foldername}'.")
        self.refresh_view()

    def change_folder_paths_dialog(self):
        foldername = self.view.get_selected_folder()
        if not foldername:
            self.view.new_log("No folder selected.")
            return
        info = self.model.folders_data.get(foldername)
        if not info:
            self.view.new_log(f"Folder '{foldername}' not found.")
            return
        result = self.view.prompt_change_paths(info['local_path'], info['usb_path'])
        if not result:
            return
        local_path, usb_path = result
        self.model.set_folder_data(foldername, local_path=local_path, usb_path=usb_path)
        self.view.new_log(f"Changed paths for '{foldername}'.")
        self.refresh_view()
    
    def remove_folder_dialog(self):
        foldername = self.view.get_selected_folder()
        if not foldername:
            self.view.new_log("No folder selected.")
            return
        reply = QMessageBox.question(self.view, 'Remove Folder', 
                                     f"Are you sure you want to remove folder '{foldername}' from tracking? This will delete its tracking files.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.model.remove_folder_from_db(foldername)
                self.view.new_log(f"Removed folder '{foldername}' from tracking.")
            except OSError as e:
                self.view.new_log(f"Error removing folder '{foldername}': {e}")
                print(f"Error removing folder '{foldername}': {e}")
            self.refresh_view()
        else:
            self.view.new_log("Folder removal cancelled.")
    
    def get_folder_details(self, foldername=None):
        if not foldername:
            foldername = self.view.get_selected_folder()
        if not foldername:
            self.view.new_log("No folder selected.")
            self.view.update_folder_details_view({})
            return
        info = self.model.get_folder_data(foldername)
        if not info:
            self.view.new_log(f"Folder '{foldername}' not found.")
            self.view.update_folder_details_view({})
            return
        self.view.update_folder_details_view(info)

    def refresh_view(self):
        self.model.load_folderlist()
        folders = self.model.get_all_folders_data()
        self.view.update_folders_view(folders)
        self.view.update_folder_details_view({})
        # self.view.new_log("View updated.")

# ----- TESTING -----

if __name__ == "__main__":

    app = QApplication(sys.argv)
    model = RepoModel()
    view = MainWindow()
    controller = MainController(model, view)
    app.aboutToQuit.connect(model.close)
    view.show()
    sys.exit(app.exec_())