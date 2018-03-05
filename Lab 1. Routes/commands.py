from abc import abstractmethod
from helpers import singleton
from PyQt5 import QtWidgets
import logging
import gpxpy
import gpxpy.gpx
from routes import RoutesCreator


class Command:

    @abstractmethod
    def execute(self, win) -> None:
        pass


@singleton
class Requester:
    pass


@singleton
class Saver:
    pass


@singleton
class Importer:
    def from_gpx(self, win):
        win.statusbar.showMessage("Please, choose file...")
        file = QtWidgets.QFileDialog.getOpenFileNames(parent=win, caption="Open file...", filter="*.gpx")
        if file == ('', ''):
            QtWidgets.QMessageBox.warning(None, "Warning", "File was not selected!",
                                          buttons=QtWidgets.QMessageBox.Ok)
            logging.warning("The route was not entered")
        else:
            with open(file[0], 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                RoutesCreator.create_route(gpx, file[0], win)
                logging.debug("The route from {0} was be loaded.".format(file[0]))
                win.statusbar.showMessage("The route from {0} was loaded.".format(file[0]))

    def from_polyline(self, win):
        win.statusbar.showMessage("Please, inter the polyline...")
        polyline, ok = QtWidgets.QInputDialog.getText(win, "Input polyline...", "",
                                                      text="soe~Hovqu@dCrk@xZpR~VpOfwBmtG")
        if ok:
            name, ok = QtWidgets.QInputDialog.getText(win, "Input title...", "",
                                                      text="MyRoute")
            if not ok:
                QtWidgets.QMessageBox.critical(None, "Entering polyline error",
                                               "Title of route was not entered!\n"
                                               "The route will be assigned a default name (MyRoute).",
                                               defaultButton=QtWidgets.QMessageBox.Ok)
                name = "MyRoute"
                logging.warning("The title of route {0} was not entered".format(polyline))

            RoutesCreator.create_route(polyline, name, win)
            logging.debug("The polyline {0} with title {1} was loaded.".format(polyline, name))
            win.statusbar.showMessage("The polyline {0} with title {1} was loaded.".format(polyline, name))
        else:
            QtWidgets.QMessageBox.warning(None, "Warning", "Polyline was not entered!",
                                          buttons=QtWidgets.QMessageBox.Ok)
            logging.warning("The route was not entered.")


@singleton
class OperationStack:
    pass


class Redo(Command):
    def __init__(self, executor=OperationStack()) -> None:
        self.stack = executor

    def execute(self, win):
        logging.debug("Redo Сommand")


class Undo(Command):
    def __init__(self, executor=OperationStack()) -> None:
        self.op_stack = executor

    def execute(self, win):
        logging.debug("Undo command")


class Save(Command):
    def __init__(self, executor=Saver()) -> None:
        self.op_stack = executor

    def execute(self, win):
        logging.debug("Save command")


class ImportGPX(Command):
    def __init__(self, executor=Importer()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("ImportGPX command")
        self.importer.from_gpx(win=win)


class ImportPolyline(Command):
    def __init__(self, executor=Importer()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("ImportPoly command")
        self.importer.from_polyline(win=win)


class FindFromGoogle(Command):
    def __init__(self, executor=Requester()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("Go command")


if __name__ == "__main__":
    pass
