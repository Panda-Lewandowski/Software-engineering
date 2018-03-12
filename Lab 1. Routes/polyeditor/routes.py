from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from math import sin, cos, acos
from polyline import decode, encode
import gpxpy
import gpxpy.gpx
import logging
import datetime



routes_pool = {}


R = 6371  # Polar radius


class Route:
    def __init__(self, source, name, win):
        self.title = None
        self.date = datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")
        self.length = 0
        self.type = type(source)
        self.polyline = None
        if self.type == gpxpy.gpx.GPX:
            self.title = name.split("/")[-1].split('.')[0]
            self.path = name
            self.length = source.length_2d()
            self.points = []
            for track in source.tracks:
                for segment in track.segments:
                    self.points += segment.points
            self.points = list(map(lambda x: [x.latitude, x.longitude], self.points))
            self.waypoints = source.waypoints
            self.polyline = encode(self.points)
        elif self.type == str:
            self.title = name
            try:
                self.points = decode(source)
            except IndexError:
                QtWidgets.QMessageBox.critical(None, "Error has occurred",
                                               "An error occurred while processing the polyline."
                                               "Please, check it.".format(type(source)))
                logging.error("An error occurred while processing the polyline.".format(type(source)))
                source, ok = QtWidgets.QInputDialog.getText(win, "Input polyline...", "",
                                                              text="soe~Hovqu@dCrk@xZpR~VpOfwBmtG")
                self.points = decode(source)

            self.points = list(map(lambda x: [x[0], x[1]], self.points))
            self.length = R * acos(sin(self.points[0][0]) * sin(self.points[-1][0]) +
                                   cos(self.points[0][0]) * cos(self.points[-1][0]) *
                                   cos(self.points[0][1] - self.points[-1][1]))
            self.polyline = source

        else:
            QtWidgets.QMessageBox.critical(None, "Unknown type of route",
                                           "An unknown route type ({0}) was selected. "
                                           "The route will not be loaded.".format(type(source)))
            logging.error("An unknown route type ({0}) was selected.".format(type(source)))

        while self.title in routes_pool.keys():
            name, ok = QtWidgets.QInputDialog.getText(win, "Input title...",
                                                      "The title was already exist. Please, enter a new one:",
                                                      text="MyRoute{0}".format(len(routes_pool)))
            if ok:
                self.title = name
        routes_pool.update({self.title: self})
        self.fill_route_table(win)

    def fill_route_table(self, win):
        r = win.routes.rowCount()
        win.routes.insertRow(r)
        title = QTableWidgetItem("{0}".format(self.title))
        length = QTableWidgetItem("{0:.3f}".format(self.length))
        time = QTableWidgetItem("{0}".format(self.date))
        win.routes.setItem(r, 0, title)
        win.routes.setItem(r, 1, length)
        win.routes.setItem(r, 2, time)
        win.stack.push({
            "Edit": {
                "title": self.title
            }
        })
        win.stack.push({
            "Edit": {
                "length": [self.title, self.length]
            }
        })
        win.stack.push({
            "Edit": {
                "date": [self.title, self.date]
            }
        })

        length.setFlags(Qt.ItemIsSelectable)
        win.routes.resizeColumnsToContents()


class RoutesCreator:  # фабричный метод
    @staticmethod
    def create_route(source, path, win):
        win.delete.setEnabled(True)
        return Route(source, path, win)

    @staticmethod
    def delete_route(win):
        items = win.routes.selectedItems()
        routes_pool.pop(win.routes.item(items[0].row(), 0).text())
        win.routes.removeRow(items[0].row())
        while win.info.rowCount() != 0:
            win.info.removeRow(0)
        while win.points.rowCount() != 0:
            win.points.removeRow(0)

        if len(routes_pool) == 0:
            win.delete.setEnabled(False)






