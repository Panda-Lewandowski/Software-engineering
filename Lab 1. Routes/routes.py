from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from math import sin, cos, acos
from polyline import decode, encode
import gpxpy
import gpxpy.gpx
import helpers
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
        win.routes.resizeColumnsToContents()

    @staticmethod
    def fill_points_table(win):
        while win.points.rowCount() != 0:
            win.points.removeRow(0)
        items = win.routes.selectedItems()
        route = routes_pool[win.routes.item(items[0].row(), 0).text()]
        for point in route.points:
            r = win.points.rowCount()
            win.points.insertRow(r)
            lat = QTableWidgetItem("{0:.5f}".format(point[0]))
            lon = QTableWidgetItem("{0:.5f}".format(point[1]))
            win.points.setItem(r, 0, lat)
            win.points.setItem(r, 1, lon)

        win.points.resizeColumnsToContents()

    @staticmethod
    def fill_property_table(win):
        while win.info.rowCount() != 0:
            win.info.removeRow(0)
        items = win.routes.selectedItems()
        route = routes_pool[win.routes.item(items[0].row(), 0).text()]
        for pr in route.__dict__:
            if pr != 'points':
                r = win.info.rowCount()
                win.info.insertRow(r)
                value = QTableWidgetItem("{0}".format(route.__dict__[pr]))
                pr = QTableWidgetItem("{0}".format(pr))
                win.info.setItem(r, 0, pr)
                win.info.setItem(r, 1, value)

        win.info.resizeColumnsToContents()

    @staticmethod
    def edit_route(win):
        items = win.routes.selectedItems()
        if items:
            for item in items:
                col = item.column()
                row = item.row()
                keys = list(routes_pool.keys())
                route = routes_pool[keys[row]]
                if col == 0:
                    replacement = {route.title: item.text()}
                    for i in routes_pool:
                        if i in replacement:
                            routes_pool[replacement[i]] = routes_pool.pop(i)
                    route.title = item.text()
                elif col == 1:
                    item.setText("{0:.3f}".format(route.length))
                elif col == 2:
                    route.date = item.text()

            Route.fill_property_table(win)

    @staticmethod
    def edit_points(win):
        items = win.routes.selectedItems()
        if items:
            route = routes_pool[win.routes.item(items[0].row(), 0).text()]
            points = win.points.selectedItems()
            if points:
                for p in points:
                    col = p.column()
                    row = p.row()
                    route.points[row][col] = float(p.text())

            route.length = R * acos(sin(route.points[0][0]) * sin(route.points[-1][0]) +
                               cos(route.points[0][0]) * cos(route.points[-1][0]) *
                               cos(route.points[0][1] - route.points[-1][1]))

            Route.fill_property_table(win)
            len_item = win.routes.item(items[0].row(), 1)
            len_item.setText("{0:.3f}".format(route.length))


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






