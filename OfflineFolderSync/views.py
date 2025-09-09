# views.py
# Handles the GUI
# What the user sees and interacts with


from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QListWidget,
    QMenuBar, QAction, QFileDialog, QMessageBox, QTextEdit
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USB Sync App")

        # Zone centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # Liste de fichiers
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        # Zone de logs
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.layout.addWidget(self.log_area)

        # Barre de menus
        self._create_menu()

    def _create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        open_action = QAction("Open Folder", self)
        quit_action = QAction("Quit", self)

        file_menu.addAction(open_action)
        file_menu.addAction(quit_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        help_menu.addAction(about_action)

        # Connecter signaux → slots
        open_action.triggered.connect(self._on_open_folder)
        quit_action.triggered.connect(self.close)
        about_action.triggered.connect(self._on_about)

    def _on_open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.log(f"Folder selected: {folder}")

    def _on_about(self):
        QMessageBox.information(self, "About", "USB Sync App\nPrototype CAI Project")

    def log(self, text):
        self.log_area.append(text)

    def update_file_list(self, files: dict):
        self.file_list.clear()
        for filename, info in files.items():
            self.file_list.addItem(f"{filename} - {info['status']}")
