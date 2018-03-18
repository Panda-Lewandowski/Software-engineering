from PyQt5 import QtWidgets, uic
from commands import Redo, Undo, ImportGPX, ImportPolyline, Remove, Fill, Edit, OperationStack
from routes import Route, RoutesCreator


class Window(QtWidgets.QMainWindow):   # Facade
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi("editor.ui", self)
        self._redo = Redo()
        self._undo = Undo()
        self._import_gpx = ImportGPX()
        self._import_poly = ImportPolyline()
        self._remove = Remove()
        self._fill = Fill()
        self._edit = Edit()

        self.stack = OperationStack()
        self.stack.win = self

        self.delete_route.setEnabled(False)
        self.delete_point.setEnabled(False)
        self.redo.setEnabled(False)
        self.undo.setEnabled(False)

        self.info.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.redo.clicked.connect(lambda: self._redo.execute(win=self))
        self.undo.clicked.connect(lambda: self._undo.execute(win=self))
        self.import_gpx.clicked.connect(lambda: self._import_gpx.execute(win=self))
        self.import_poly.clicked.connect(lambda: self._import_poly.execute(win=self))
        self.delete_route.clicked.connect(lambda: self._remove.execute(self, "route"))
        self.delete_point.clicked.connect(lambda: self._remove.execute(self, "point"))

        self.routes.cellClicked.connect(lambda: self._fill.execute(self))
        self.routes.cellChanged.connect(lambda: self._edit.execute(self))
        self.points.cellChanged.connect(lambda: self._edit.execute(self))
        self.points.cellClicked.connect(lambda: self._edit.execute(self))


def run_editor():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        run_editor()
    except Exception:
        QtWidgets.QMessageBox.critical(None, "Suddenly...", "An error occurred. \n Please restart the program.",
                                       defaultButton=QtWidgets.QMessageBox.Ok)
