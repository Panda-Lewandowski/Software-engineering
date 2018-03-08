from abc import abstractmethod
from helpers import singleton
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
import logging
import gpxpy
import gpxpy.gpx
from math import sin, cos, acos
from routes import routes_pool, R, RoutesCreator

HISTORY = []



class Command:

    @abstractmethod
    def execute(self, win) -> None:
        pass

    @abstractmethod
    def cancel(self, win) -> None:
        pass


@singleton
class OperationStack:
    def push(self, elem):
        print(elem, "\n")
        HISTORY.append(elem)

    def pop(self):
        HISTORY.pop()


class Redo(Command):
    def execute(self, elem):
        logging.debug("Redo Сommand")

    def cancel(self, win) -> None:
        pass


class Undo(Command):
    def execute(self, win):
        logging.debug("Undo command")

    def cancel(self, win) -> None:
        pass


@singleton
class Filler:
    def fill_tables(self, win):
        while win.points.rowCount() != 0:
            win.points.removeRow(0)
        while win.info.rowCount() != 0:
            win.info.removeRow(0)

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

        for pr in route.__dict__:
            if pr != 'points':
                r = win.info.rowCount()
                win.info.insertRow(r)
                value = QTableWidgetItem("{0}".format(route.__dict__[pr]))
                pr = QTableWidgetItem("{0}".format(pr))
                win.info.setItem(r, 0, pr)
                win.info.setItem(r, 1, value)

        win.info.resizeColumnsToContents()

        win.stack.push({
            "Fill": {
                "fill_tables": route
            }
        })


@singleton
class Editor:
    def edit_route(self, win):
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
                    item_to_change = win.info.findItems("title", Qt.MatchFixedString)
                    temp = win.info.item(item_to_change[0].row(), 1)
                    temp.setText("{0}".format(route.title))
                    win.stack.push({
                        "Edit": {
                            "title": route.title
                        }
                    })
                elif col == 1:
                    route.length = float(item.text())
                    item_to_change = win.info.findItems("length", Qt.MatchFixedString)
                    temp = win.info.item(item_to_change[0].row(), 1)
                    temp.setText("{0}".format(route.length))
                    win.stack.push({
                        "Edit": {
                            "length": route.length
                        }
                    })
                elif col == 2:
                    route.date = item.text()
                    item_to_change = win.info.findItems("date", Qt.MatchFixedString)
                    temp = win.info.item(item_to_change[0].row(), 1)
                    temp.setText("{0}".format(route.date))
                    win.stack.push({
                        "Edit": {
                            "date": route.date
                        }
                    })

    def edit_points(self, win):
        items = win.routes.selectedItems()
        if items:
            route = routes_pool[win.routes.item(items[0].row(), 0).text()]
            points = win.points.selectedItems()
            if points:
                for p in points:
                    col = p.column()
                    row = p.row()
                    route.points[row][col] = float(p.text())

                    win.stack.push({
                        "Edit": {
                            "point": [row, col, p.text]
                        }
                    })

                route.length = R * acos(sin(route.points[0][0]) * sin(route.points[-1][0]) +
                                        cos(route.points[0][0]) * cos(route.points[-1][0]) *
                                        cos(route.points[0][1] - route.points[-1][1]))

                win.stack.push({
                    "Edit": {
                        "length": route.length
                    }
                })

                item_to_change = win.info.findItems("length", Qt.MatchFixedString)
                temp = win.info.item(item_to_change[0].row(), 1)
                temp.setText("{0}".format(route.length))
                len_item = win.routes.item(items[0].row(), 1)
                len_item.setText("{0:.3f}".format(route.length))


@singleton
class Remover:
    def delete_selected_route(self, win):
        items = win.routes.selectedItems()
        win.stack.push({
            "Remove": {
                "route": win.routes.item(items[0].row(), 0).text()
            }
        })
        routes_pool.pop(win.routes.item(items[0].row(), 0).text())
        win.routes.removeRow(items[0].row())
        while win.info.rowCount() != 0:
            win.info.removeRow(0)
        while win.points.rowCount() != 0:
            win.points.removeRow(0)

        if len(routes_pool) == 0:
            win.delete.setEnabled(False)


@singleton
class Importer:
    def from_gpx(self, win):
        win.statusbar.showMessage("Please, choose file...")
        file = QtWidgets.QFileDialog.getOpenFileName(parent=win, caption="Open file...", filter="*.gpx")
        if file == ('', ''):
            QtWidgets.QMessageBox.warning(None, "Warning", "File was not selected!",
                                          buttons=QtWidgets.QMessageBox.Ok)
            logging.warning("The route was not entered")
        else:
            print(file[0])
            with open(file[0], 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                RoutesCreator.create_route(gpx, file[0], win)
                logging.debug("The route from {0} was be loaded.".format(file[0]))
                win.statusbar.showMessage("The route from {0} was loaded.".format(file[0]))

                win.stack.push({
                "ImportGPX": {
                    "import": file[0].split("/")[-1].split('.')[0]
                }
            })

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

            win.stack.push({
                "ImportPolyline": {
                    "import": name
                }
            })

        else:
            QtWidgets.QMessageBox.warning(None, "Warning", "Polyline was not entered!",
                                          buttons=QtWidgets.QMessageBox.Ok)
            logging.warning("The route was not entered.")


class ImportGPX(Command):
    def __init__(self, executor=Importer()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("ImportGPX command")
        self.importer.from_gpx(win=win)

    def cancel(self, win) -> None:
        pass


class ImportPolyline(Command):
    def __init__(self, executor=Importer()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("ImportPoly command")
        self.importer.from_polyline(win=win)

    def cancel(self, win) -> None:
        pass


class Fill(Command):
    def __init__(self, executor=Filler()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("Fill command")
        try:
            self.importer.fill_tables(win=win)
        except IndexError:
            pass

    def cancel(self, win) -> None:
        pass


class Edit(Command):
    def __init__(self, executor=Editor()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("Edit command")
        try:
            if win.points.selectedItems():
                self.importer.edit_points(win)
            if win.routes.selectedItems():
                self.importer.edit_route(win)
        except IndexError:
            pass

    def cancel(self, win) -> None:
        pass


class Remove(Command):
    def __init__(self, executor=Remover()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("Delete command")
        self.importer.delete_selected_route(win=win)

    def cancel(self, win) -> None:
        pass


if __name__ == "__main__":
    pass
