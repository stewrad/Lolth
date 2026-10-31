import os,sys
if sys.platform.startswith('linux'):
    os.environ.setdefault('QT_QPA_PLATFORM','xcb')
from PyQt6.QtWidgets import QApplication
from .main_window import MainWindow

def main():
    app=QApplication(sys.argv)
    app.setStyle('Fusion')
    window=MainWindow()
    window.show()
    return app.exec()

if __name__=='__main__':
    sys.exit(main())
