from PyQt6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGridLayout, QComboBox, QTreeView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont, QFileSystemModel


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
        self.setMinimumSize(800, 600)
        # Fonts parameters
        self.fontfamily = "Arial"
        self.title = QFont(self.fontfamily, 12, QFont.Weight.Bold)
        self.label = QFont(self.fontfamily, 10)
        self.note = QFont(self.fontfamily, 18)

        ## FOLDER SELECTION WIDGET
        self.folderselection_label = QLabel("Select Folder to Track")
        self.folderselection_label.setFont(self.label)
        self.folderselector = QComboBox() # OBSERVER
        self.addbutton = QPushButton("Add Folder")
        # TODO!(0) link add button to feature
        self.removebutton = QPushButton("Remove Selected Folder")
        # TODO!(0) link remove button to feature
        # TODO!(1) deactivate remove button if no folder is selected
        # Layout
        self.folderselection_layout = QHBoxLayout()
        self.folderselection_layout.addWidget(self.folderselection_label)
        self.folderselection_layout.addWidget(self.folderselector)
        self.folderselection_layout.addWidget(self.addbutton)
        self.folderselection_layout.addWidget(self.removebutton)

        ## FILE TREE WIDGET
        # self.filetree_label = QLabel("Folder Content")
        # self.filetree_label.setFont(self.label)
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
        self.localpath_label.setFont(self.label)
        self.localpath = QLineEdit("") #TODO!(0) read path # OBSERVER
        self.localpath.setReadOnly(True)
        # Remote Path
        self.remotepath_label = QLabel("Remote Path")
        self.remotepath_label.setFont(self.label)
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
        print(f"Updating view.")
        self.update_folderlist()
        self.update_filetree()

    def update_folderlist(self, folderlist):
        self.folderselector.clear()
        self.folderselector.addItems(folderlist)
    
    def update_filetree(self, local_path, remote_path):
        self.local_tree_model.setRootPath(local_path)
        self.remote_tree_model.setRootPath(remote_path)
        self.local_filetree.setModel(self.local_tree_model)
        self.remote_filetree.setModel(self.remote_tree_model)

if __name__ == "__main__":

    print(">> Testing views.py <<")

    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
