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
        file = QtWidgets.QFileDialog.getOpenFileName(parent=win, caption="Open file...", filter="*.gpx")
        gpx_file = open(file[0], 'r')
        gpx = gpxpy.parse(gpx_file)
        name = file[0].split("/")[-1]
        RoutesCreator.create_route(gpx, name, win)


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
    def __init__(self, executor=Importer) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("ImportPoly command")


class FindFromGoogle(Command):
    def __init__(self, executor=Requester()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("Go command")


if __name__ == "__main__":
    pass
