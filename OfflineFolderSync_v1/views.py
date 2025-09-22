# views.py
# Handles the GUI
# What the user sees and interacts with

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QListWidget, QPushButton, QInputDialog,
    QMenuBar, QAction, QFileDialog, QMessageBox, QTextEdit, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Header font (for section labels)
header_font = QFont()
header_font.setPointSize(14)  # Larger size for headers
header_font.setBold(True)     # Optional: make headers bold

# Content font (for lists, text fields, etc.)
content_font = QFont()
content_font.setPointSize(11)  # Smaller size for content


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.controller = None  # To be set by controller
        self.setWindowTitle("USB Folders Sync")

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QGridLayout()
        central_widget.setLayout(self.layout)

        # List of tracked folders
        folderlist_widget = QWidget()
        folderlist_layout = QVBoxLayout()
        self.folder_list_label = QLabel("Tracked Folders")
        folderlist_layout.addWidget(self.folder_list_label)
        self.folder_list = QListWidget()
        folderlist_layout.addWidget(self.folder_list)
        folderlist_widget.setLayout(folderlist_layout)
        self.layout.addWidget(folderlist_widget, 0, 0)

        # Selected folder details
        details_widget = QWidget()
        details_layout = QVBoxLayout()
        self.details_label = QLabel("Folder Details")
        details_layout.addWidget(self.details_label)
        # self.folder_name_label = QLabel()
        # self.folder_status_label = QLabel()
        self.local_path_label = QTextEdit()
        self.usb_path_label = QTextEdit()
        # self.local_path_label.setReadOnly(True)
        # self.usb_path_label.setReadOnly(True)
        # details_layout.addWidget(self.folder_name_label)
        details_layout.addWidget(self.local_path_label)
        details_layout.addWidget(self.usb_path_label)
        details_widget.setLayout(details_layout)
        self.layout.addWidget(details_widget, 0, 1)
        
        # Action buttons
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        self.add_folder_button = QPushButton("Add New Folder")
        self.change_paths_button = QPushButton("Change Paths")
        self.remove_folder_button = QPushButton("Remove Folder")
        buttons_layout.addWidget(self.add_folder_button)
        buttons_layout.addWidget(self.change_paths_button)
        buttons_layout.addWidget(self.remove_folder_button)
        buttons_widget.setLayout(buttons_layout)
        self.layout.addWidget(buttons_widget, 0, 2)

        # Log area
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        self.log_label = QLabel("Log")
        log_layout.addWidget(self.log_label)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        log_widget.setLayout(log_layout)
        self.layout.addWidget(log_widget, 1, 0, 1, 2)

        # Apply fonts
        self.folder_list_label.setFont(header_font)
        self.details_label.setFont(header_font)
        self.log_label.setFont(header_font)

        self.folder_list.setFont(content_font)
        self.local_path_label.setFont(content_font)
        self.usb_path_label.setFont(content_font)
        self.log_area.setFont(content_font)
        self.add_folder_button.setFont(content_font)
        self.change_paths_button.setFont(content_font)
        self.remove_folder_button.setFont(content_font)

        # stretch factors
        self.layout.setColumnStretch(0, 1)  # folder list: less stretch
        self.layout.setColumnStretch(1, 3)  # details: more stretch

        # Menu bar
        # self._create_menu()

        # Connect buttons to slots (controller will set these)
        self.add_folder_button.clicked.connect(lambda: None)
        self.change_paths_button.clicked.connect(lambda: None)
        self.remove_folder_button.clicked.connect(lambda: None)

        # Connect folder selection details update
        self.folder_list.itemSelectionChanged.connect(self.on_folder_selected)


    # CALLBACKS

    def set_add_folder_callback(self, callback):
        self.add_folder_button.clicked.disconnect()
        self.add_folder_button.clicked.connect(callback)

    def set_change_paths_callback(self, callback):
        self.change_paths_button.clicked.disconnect()
        self.change_paths_button.clicked.connect(callback)
    
    def set_remove_folder_callback(self, callback):
        self.remove_folder_button.clicked.disconnect()
        self.remove_folder_button.clicked.connect(callback)

    # DIALOGS

    def get_selected_folder(self):
        current = self.folder_list.currentItem()
        if current:
            return current.text().split(' - ')[0]
        return None
    
    def on_folder_selected(self):
        self.controller.get_folder_details(foldername=self.get_selected_folder())

    def prompt_add_folder(self):
        local_path = QFileDialog.getExistingDirectory(self, "Select local path")
        if not local_path:
            QMessageBox.information(self, "Add Folder", "No local path selected.")
            return None
        usb_path = QFileDialog.getExistingDirectory(self, "Select USB path")
        if not usb_path:
            QMessageBox.information(self, "Add Folder", "No USB path selected.")
            return None
        foldername, ok1 = QInputDialog.getText(self, "Add Folder", "Folder name:")
        if not ok1 or not foldername:
            return None
        return foldername, local_path, usb_path

    def prompt_change_paths(self, current_local, current_usb):
        local_path = QFileDialog.getExistingDirectory(self, "Select new local path", current_local)
        if not local_path:
            QMessageBox.information(self, "Change Path", "No local path selected.")
            return None
        usb_path = QFileDialog.getExistingDirectory(self, "Select new USB path", current_usb)
        if not usb_path:
            QMessageBox.information(self, "Change Path", "No USB path selected.")
            return None
        return local_path, usb_path


    def update_folders_view(self, folders: dict):
        self.folder_list.blockSignals(True)
        self.folder_list.clear()
        for foldername, info in folders.items():
            self.folder_list.addItem(f"{foldername} - {info['status']}")
        self.folder_list.blockSignals(False)

    def update_folder_details_view(self, details: dict):
        # Clear existing details
        # self.folder_name_label.clear()
        self.local_path_label.clear()
        self.usb_path_label.clear()

        # Update with new details
        # self.folder_name_label.setText(details.get("name", "Unknown"))
        self.local_path_label.setText(details.get("local_path", ""))
        self.usb_path_label.setText(details.get("usb_path", ""))


    # def _create_menu(self):
    #     menubar = self.menuBar()

    #     file_menu = menubar.addMenu("File")
    #     open_action = QAction("Open Folder", self)
    #     quit_action = QAction("Quit", self)

    #     file_menu.addAction(open_action)
    #     file_menu.addAction(quit_action)

    #     help_menu = menubar.addMenu("Help")
    #     about_action = QAction("About", self)
    #     help_menu.addAction(about_action)

    #     # Connecter signaux → slots
    #     quit_action.triggered.connect(self.close)


    def new_log(self, text):
        self.log_area.clear()
        self.log_area.append(text)

