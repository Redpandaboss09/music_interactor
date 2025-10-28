import sys
from PySide6.QtWidgets import QApplication
from ..core.config import Settings
from .main_window import MainWindow

def main():
    s = Settings.from_file()
    app = QApplication(sys.argv)
    window = MainWindow(settings=s)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()