import sys
from PyQt5.QtWidgets import QApplication
from gui import GraphGUI


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphGUI()
    window.showMaximized()
    window.show()
    sys.exit(app.exec_())

