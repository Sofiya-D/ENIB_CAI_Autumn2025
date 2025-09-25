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
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGridLayout, QComboBox, QTreeView
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QAction, QFont, QFileSystemModel
    if __name__ == "__main__":
        print(f"Your Python version is: {major}.{minor}")
        print("PyQt6 should work fine!")



# OBSERVER DESIGN PATTERN - OBSERVER
# Rôle d'un "observateur" (Observer) :
# faire des mises à jour (update(subject)) en cas de
# notification d'un subject auquel il est attaché
class Observer:
    def update(self,subject):
        raise NotImplementedError
    # EXAMPLE:
    # def update(self,subject):
    #     print("Observer :",self.name)
    #     print("Subject data :", subject.get_data())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ## VISUAL PARAMETERS
        self.setWindowTitle("Offline Folder Synchronization")
        self.setMinimumSize(500, 300)
        # Fonts parameters
        self.fontfamily = "Arial"
        self.titlefont = QFont(self.fontfamily, 12, QFont.Weight.Bold)
        self.labelfont = QFont(self.fontfamily, 10)
        self.notefont = QFont(self.fontfamily, 18)

        ## FOLDER SELECTION WIDGET
        self.folderselection_label = QLabel("Select Folder to Track")
        self.folderselection_label.setFont(self.labelfont)
        self.folderselector = QComboBox() # OBSERVER
        self.folderselector.maxVisibleItems = 9
        self.folderselector.insertPolicy = QComboBox.InsertPolicy.InsertAlphabetically
        self.addfolderbutton = QPushButton("Add Folder")
        # TODO!(0) link add button to feature
        self.removefolderbutton = QPushButton("Remove Selected Folder")
        # TODO!(0) link remove button to feature
        # TODO!(1) deactivate remove button if no folder is selected
        # Layout
        self.folderselection_layout = QHBoxLayout()
        self.folderselection_layout.addWidget(self.folderselection_label)
        self.folderselection_layout.addWidget(self.folderselector)
        self.folderselection_layout.addWidget(self.addfolderbutton)
        self.folderselection_layout.addWidget(self.removefolderbutton)

        ## FILE TREE WIDGET
        # self.filetree_label = QLabel("Folder Content")
        # self.filetree_label.setFont(self.labelfont)
        self.local_tree_model = QFileSystemModel()
        self.remote_tree_model = QFileSystemModel()
        self.local_filetree = QTreeView() # OBSERVER
        self.remote_filetree = QTreeView() # OBSERVER
        # Layout
        self.filetree_layout = QHBoxLayout()
        # self.filetree_layout.addWidget(self.filetree_label)
        self.filetree_layout.addWidget(self.local_filetree)
        self.filetree_layout.addWidget(self.remote_filetree)

        ## DETAILS WIDGET
        # Local Path
        self.localpath_label = QLabel("Local Path")
        self.localpath_label.setFont(self.labelfont)
        self.localpath = QLineEdit("") #TODO!(0) read path # OBSERVER
        self.localpath.setReadOnly(True)
        # Remote Path
        self.remotepath_label = QLabel("Remote Path")
        self.remotepath_label.setFont(self.labelfont)
        self.remotepath = QLineEdit("") #TODO!(0) read path # OBSERVER
        self.remotepath.setReadOnly(True)
        # Other
        self.changepathbutton = QPushButton("Change Paths")
        self.changenamebutton = QPushButton("Change Name")
        # Layout
        self.details_layout = QGridLayout()
        self.details_layout.addWidget(self.localpath_label, 0, 0)
        self.details_layout.addWidget(self.localpath, 0, 1)
        self.details_layout.addWidget(self.remotepath_label, 1, 0)
        self.details_layout.addWidget(self.remotepath, 1, 1)
        self.details_layout.addWidget(self.changenamebutton, 2, 0)
        self.details_layout.addWidget(self.changepathbutton, 2, 1)

        ## LAYOUT
        self.mainwidget = QWidget()
        self.mainlayout = QGridLayout()
        self.mainwidget.setLayout(self.mainlayout)
        self.mainlayout.addLayout(self.folderselection_layout, 0, 0, 1, 3)
        self.mainlayout.addLayout(self.filetree_layout, 1, 0, 2, 1)
        self.mainlayout.addLayout(self.details_layout, 1, 1, 1, 2)
        self.setCentralWidget(self.mainwidget)
        # TODO!(1) spacing a little more the folder selection and the content below it to improve visual comfort
        # TODO!(1) fix the filetree width taking more space than allowed


    def update(self, subject):
        print(type(self).__name__+".update()")
        folderlist = subject.get_foldernames_list()
        local_path = subject.get_local_folder().get_path()
        remote_path = subject.get_remote_folder().get_path()
        if DEBUG:
            print(f"local path: {local_path} \t remote path: {remote_path}")
        self.update_folderlist(new_folderlist=folderlist)
        self.update_filetree(local_path=local_path, remote_path=remote_path)
        self.update_paths_views(local_path=local_path, remote_path=remote_path)
             

    def update_folderlist(self, new_folderlist=[]):
        # TODO!(1) Fix the order of the list changing on different runs...
        new_folderlist = [""]+sorted(new_folderlist)
        selected_folder = self.folderselector.currentText()
        old_folderlist = [self.folderselector.itemText(i) for i in range(self.folderselector.count())]
        if selected_folder not in new_folderlist:
            index = self.folderselector.findText(selected_folder)
            self.folderselector.removeItem(index)
        new_items = set(new_folderlist) - set(old_folderlist)
        self.folderselector.addItems(new_items)
    

    def update_filetree(self, local_path=None, remote_path=None):
        print(type(self).__name__+".update_filetree()")
        print(f"local path: {local_path} \t remote path: {remote_path}")
        if local_path is None:
            self.local_filetree.setModel(None)
        else:
            self.local_tree_model.setRootPath(local_path)
            self.local_filetree.setModel(self.local_tree_model)
        if remote_path is None:
            self.remote_filetree.setModel(None)
        else:
            self.remote_tree_model.setRootPath(remote_path)
            self.remote_filetree.setModel(self.remote_tree_model)
    
    def update_paths_views(self, local_path=None, remote_path=None):
        self.localpath.setText(local_path)
        self.remotepath.setText(remote_path)


if __name__ == "__main__":

    print(">> Testing views.py <<")

    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
