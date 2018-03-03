from PyQt5 import QtWidgets, uic
import gpxpy
import polyline

# https://gist.github.com/signed0/2031157


class Window(QtWidgets.QMainWindow):   # Facade
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi("editor.ui", self)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
