# coding: utf-8
DEBUG=False


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


from controllers import MainController


app = QApplication(sys.argv)

controller = MainController()
controller.show()  

sys.exit(app.exec())

