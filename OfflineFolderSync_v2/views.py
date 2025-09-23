import sys
from PyQt6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMenu, QGridLayout, QComboBox, QListWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont


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
        self.folderselection = QComboBox()
        self.addbutton = QPushButton("Add Folder")
        # TODO!(0) link add button to feature
        self.removebutton = QPushButton("Remove Selected Folder")
        # TODO!(0) link remove button to feature
        # TODO!(1) deactivate remove button if no folder is selected
        # Layout
        self.folderselection_layout = QHBoxLayout()
        self.folderselection_layout.addWidget(self.folderselection_label)
        self.folderselection_layout.addWidget(self.folderselection)
        self.folderselection_layout.addWidget(self.addbutton)
        self.folderselection_layout.addWidget(self.removebutton)


        ## FILE TREE WIDGET
        # self.filetree_label = QLabel("Folder Content")
        # self.filetree_label.setFont(self.label)
        self.filetree = QListWidget()
        # Layout
        self.filetree_layout = QVBoxLayout()
        # self.filetree_layout.addWidget(self.filetree_label)
        self.filetree_layout.addWidget(self.filetree)


        ## DETAILS WIDGET
        # Local Path
        self.localpath_label = QLabel("Local Path")
        self.localpath_label.setFont(self.label)
        self.localpath = QLineEdit("") #TODO!(0) read path
        self.localpath.setReadOnly(True)
        # Remote Path
        self.remotepath_label = QLabel("Remote Path")
        self.remotepath_label.setFont(self.label)
        self.remotepath = QLineEdit("") #TODO!(0) read path
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



if __name__ == "__main__":

    print(">> Testing views.py <<")

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
