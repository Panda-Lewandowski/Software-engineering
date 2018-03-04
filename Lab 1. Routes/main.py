from PyQt5 import QtWidgets, uic
from commands import Redo, Undo, Save, FindFromGoogle, ImportGPX, ImportPolyline
# https://gist.github.com/signed0/2031157


class Window(QtWidgets.QMainWindow):   # Facade
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi("editor.ui", self)
        self._redo = Redo()
        self._undo = Undo()
        self._go = FindFromGoogle()
        self._import_gpx = ImportGPX()
        self._import_poly = ImportPolyline()
        self._save = Save()
        # self._update =

        self.redo.clicked.connect(lambda: self._redo.execute(win=self))
        self.undo.clicked.connect(lambda: self._undo.execute(win=self))
        self.go.clicked.connect(lambda: self._go.execute(win=self))
        self.import_gpx.clicked.connect(lambda: self._import_gpx.execute(win=self))
        self.import_poly.clicked.connect(lambda: self._import_poly.execute(win=self))
        self.save.clicked.connect(lambda: self._save.execute(win=self))
        # self.update.clicked.connect(self._redo.execute())


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
