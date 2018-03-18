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
    def execute(self, *args) -> None:
        pass

    @abstractmethod
    def cancel(self, *args) -> None:
        pass


@singleton
class OperationStack:
    def __init__(self):
        self.win = None
        self.pointer = None

    def push(self, elem):
        if len(HISTORY) == 0:
            self.win.undo.setEnabled(True)
            self.pointer = -1
        else:
            self.win.redo.setEnabled(True)

        self.pointer += 1
        # HISTORY.append(elem)
        HISTORY.insert(self.pointer, elem)

    def pop(self):
        if len(HISTORY) != 0:
            self.win.redo.setEnabled(True)

        self.pointer -= 1
        return HISTORY[self.pointer + 1]


class Redo(Command):
    def execute(self, win):
        logging.debug("Redo Сommand")
        if len(HISTORY) <= win.stack.pointer + 1:
            return
        win.stack.pointer += 1
        act = HISTORY[win.stack.pointer]
        key = list(act.keys())[0]
        sub = act[key]

        if key == "ImportPolyline":
            print('lolool')

        elif key == "ImportGPX":
            pass

        elif key == "Edit":
            if list(sub.keys())[0] == "title":
                for i in range(win.stack.pointer-1, -1, -1):
                    key = list(HISTORY[i].keys())[0]
                    if key == "Edit":
                        conf = HISTORY[i]['Edit']
                        key_c = list(conf.keys())[0]
                        if key_c == 'title':
                            print(conf['title'])
                            route = routes_pool[conf['title']]
                            item_to_change = win.info.findItems("title", Qt.MatchFixedString)
                            temp = win.info.item(item_to_change[0].row(), 1)
                            temp.setText("{0}".format(sub['title']))
                            item_to_change = win.routes.findItems(route.title, Qt.MatchFixedString)
                            temp = win.routes.item(item_to_change[0].row(), 0)
                            temp.setText("{0}".format(sub['title']))
                            route.title = sub['title']
                            break

            elif list(sub.keys())[0] == "date":
                for i in range(win.stack.pointer-1, -1, -1):
                    key = list(HISTORY[i].keys())[0]
                    if key == "Edit":
                        conf = HISTORY[i]['Edit']
                        key_c = list(conf.keys())[0]
                        if key_c == 'date':
                            route = routes_pool[conf['date'][0]]

                            item_to_change = win.routes.findItems(route.date, Qt.MatchFixedString)
                            temp = win.routes.item(item_to_change[0].row(), 2)
                            temp.setText("{0}".format(sub['date'][1]))
                            item_to_change = win.info.findItems("date", Qt.MatchFixedString)
                            temp = win.info.item(item_to_change[0].row(), 1)
                            temp.setText("{0}".format(sub['date'][1]))
                            route.date = sub['date'][1]
                            break
            elif list(sub.keys())[0] == "point":
                route = routes_pool[sub['point'][0]]
                route.points[sub['point'][1]][sub['point'][2]] = sub['point'][3]
                win._fill.execute(win)
            elif list(sub.keys())[0] == "length":
                for i in range(win.stack.pointer-1, -1, -1):
                    key = list(HISTORY[i].keys())[0]
                    if key == "Edit":
                        conf = HISTORY[i]['Edit']
                        key_c = list(conf.keys())[0]
                        if key_c == 'length':
                            route = routes_pool[conf['length'][0]]

                            item_to_change = win.routes.findItems("{0:.3f}".format(route.length), Qt.MatchContains)
                            temp = win.routes.item(item_to_change[0].row(), 1)
                            temp.setText("{0:.3f}".format(sub['length'][1]))

                            item_to_change = win.info.findItems("length", Qt.MatchFixedString)
                            temp = win.info.item(item_to_change[0].row(), 1)
                            temp.setText("{0}".format(sub['length'][1]))
                            route.length = sub['length'][1]

                            act = HISTORY[-2]['Edit']
                            try:
                                route = routes_pool[act['point'][0]]
                                route.points[act['point'][1]][act['point'][2]] = act['point'][3]
                                win._fill.execute(win)
                            except KeyError:
                                pass

        elif key == "Remove":
            if list(sub.keys())[0] == "Point":
                route = routes_pool[sub['Point'][0]]
                route.points.pop(sub['Point'][1])
                win.points.removeRow(sub['Point'][1])
            elif list(sub.keys())[0] == "GPX":
                route = sub['GPX']
                items = win.routes.findItems(route.title, Qt.MatchFixedString)
                win.routes.removeRow(items[0].row())
                while win.info.rowCount() != 0:
                    win.info.removeRow(0)
                while win.points.rowCount() != 0:
                    win.points.removeRow(0)

                if len(routes_pool) == 0:
                    win.delete_route.setEnabled(False)
            elif list(sub.keys())[0] == "Polyline":
                route = sub['Polyline']
                items = win.routes.findItems(route.title, Qt.MatchFixedString)
                win.routes.removeRow(items[0].row())
                while win.info.rowCount() != 0:
                    win.info.removeRow(0)
                while win.points.rowCount() != 0:
                    win.points.removeRow(0)

                if len(routes_pool) == 0:
                    win.delete_route.setEnabled(False)

    def cancel(self, win) -> None:
        pass


class Undo(Command):
    def execute(self, win):
        logging.debug("Undo command")
        act = win.stack.pop()
        key = list(act.keys())[0]

        if key == "ImportPolyline":
            win._import_poly.cancel(win, act[key]['import'])

        elif key == "ImportGPX":
            win._import_gpx.cancel(win, act[key]['import'])

        elif key == "Edit":
            win._edit.cancel(win, act[key])

        elif key == "Remove":
            win._remove.cancel(win, act[key])

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

        win.delete_point.setEnabled(True)

        for pr in route.__dict__:
            if pr != 'points':
                r = win.info.rowCount()
                win.info.insertRow(r)
                value = QTableWidgetItem("{0}".format(route.__dict__[pr]))
                pr = QTableWidgetItem("{0}".format(pr))
                win.info.setItem(r, 0, pr)
                win.info.setItem(r, 1, value)

        win.info.resizeColumnsToContents()


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
                    if route.title != item.text():
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
                elif col == 2:
                    if route.date != item.text():
                        route.date = item.text()
                        item_to_change = win.info.findItems("date", Qt.MatchFixedString)
                        temp = win.info.item(item_to_change[0].row(), 1)
                        temp.setText("{0}".format(route.date))
                        win.stack.push({
                            "Edit": {
                                "date": [route.title, route.date]
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
                    if route.points[row][col] != float(p.text()):

                        win.stack.push({
                            "Edit": {
                                "point": [route.title, row, col, float(p.text()), route.points[row][col]]
                            }
                        })

                        route.points[row][col] = float(p.text())

                length = R * acos(sin(route.points[0][0]) * sin(route.points[-1][0]) +
                                  cos(route.points[0][0]) * cos(route.points[-1][0]) *
                                  cos(route.points[0][1] - route.points[-1][1]))

                if route.length != length:
                    route.length = length

                    win.stack.push({
                        "Edit": {
                            "length": [route.title, route.length]
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

        if len(items) == 0:
            QtWidgets.QMessageBox.warning(None, "Warning", "Routes was not selected!",
                                          buttons=QtWidgets.QMessageBox.Ok)
            return

        route = routes_pool.pop(win.routes.item(items[0].row(), 0).text())
        if route.type == gpxpy.gpx.GPX:
            win.stack.push({
                "Remove": {
                    "GPX": route
                }
            })
        elif route.type == str:
            win.stack.push({
                "Remove": {
                    "Polyline": route
                }
            })
        win.routes.removeRow(items[0].row())
        while win.info.rowCount() != 0:
            win.info.removeRow(0)
        while win.points.rowCount() != 0:
            win.points.removeRow(0)

        if len(routes_pool) == 0:
            win.delete_route.setEnabled(False)
            win.delete_point.setEnabled(False)

    def delete_selected_point(self, win):
        items = win.routes.selectedItems()
        route = routes_pool[win.routes.item(items[0].row(), 0).text()]

        items = win.points.selectedItems()
        for i in items:
            win.stack.push({
                "Remove": {
                    "Point": [route.title, i.row(), route.points[i.row()]]
                }
            })
            route.points.pop(i.row())
            win.points.removeRow(i.row())

        if len(route.points) == 0:
            win.delete_point.setEnabled(False)


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
            win.stack.push({
                "ImportPolyline": {
                    "import": name
                }
            })
            logging.debug("The polyline {0} with title {1} was loaded.".format(polyline, name))
            win.statusbar.showMessage("The polyline {0} with title {1} was loaded.".format(polyline, name))

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

    def cancel(self, win, name) -> None:
        logging.debug("ImportGPX Сommand Cancel")
        item = win.routes.findItems(name, Qt.MatchFixedString)[0]
        item.setSelected(True)
        win.delete.click()


class ImportPolyline(Command):
    def __init__(self, executor=Importer()) -> None:
        self.importer = executor

    def execute(self, win):
        logging.debug("ImportPoly command")
        self.importer.from_polyline(win=win)

    def cancel(self, win, name) -> None:
        logging.debug("ImportPoly Сommand Cancel")
        item = win.routes.findItems(name, Qt.MatchFixedString)[0]
        item.setSelected(True)
        win.delete.click()


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
        logging.debug("Fill Сommand Cancel")


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

    def cancel(self, win, act) -> None:
        logging.debug("Edit Сommand Cancel")
        sub = list(act.keys())[0]
        if sub == "title" or sub == "date":
            for i in range(win.stack.pointer, -1, -1):
                key = list(HISTORY[i].keys())[0]
                if key == "Edit":
                    conf = HISTORY[i]['Edit']
                    key_c = list(conf.keys())[0]
                    if key_c == 'title' == sub:
                        value = conf[sub]
                        route = routes_pool[act['title']]
                        replacement = {route.title: value}
                        for i in routes_pool:
                            if i in replacement:
                                routes_pool[replacement[i]] = routes_pool.pop(i)

                        item_to_change = win.routes.findItems(route.title, Qt.MatchFixedString)
                        temp = win.routes.item(item_to_change[0].row(), 0)
                        temp.setText("{0}".format(value))

                        route.title = value

                        item_to_change = win.info.findItems("title", Qt.MatchFixedString)
                        temp = win.info.item(item_to_change[0].row(), 1)
                        temp.setText("{0}".format(route.title))

                    if key_c == "date" == sub:
                        value = conf[sub][1]
                        route = routes_pool[conf[sub][0]]

                        item_to_change = win.routes.findItems(route.date, Qt.MatchFixedString)
                        temp = win.routes.item(item_to_change[0].row(), 2)
                        temp.setText("{0}".format(value))

                        route.date = value

                        item_to_change = win.info.findItems("date", Qt.MatchFixedString)
                        temp = win.info.item(item_to_change[0].row(), 1)
                        temp.setText("{0}".format(route.date))

        elif sub == "point":
            route = routes_pool[act['point'][0]]
            route.points[act['point'][1]][act['point'][2]] = act['point'][4]
            win._fill.execute(win)

        elif sub == "length":
            for i in range(win.stack.pointer, -1, -1):
                key = list(HISTORY[i].keys())[0]
                if key == "Edit":
                    conf = HISTORY[i]['Edit']
                    key_c = list(conf.keys())[0]
                    if key_c == 'length':
                        value = conf[sub][1]
                        route = routes_pool[conf[sub][0]]

                        item_to_change = win.routes.findItems("{0:.3f}".format(route.length), Qt.MatchContains)
                        temp = win.routes.item(item_to_change[0].row(), 1)
                        temp.setText("{0:.3f}".format(value))

                        route.length = value

                        item_to_change = win.info.findItems("length", Qt.MatchFixedString)
                        temp = win.info.item(item_to_change[0].row(), 1)
                        temp.setText("{0}".format(route.length))

                        act = HISTORY[-2]['Edit']
                        try:
                            route = routes_pool[act['point'][0]]
                            route.points[act['point'][1]][act['point'][2]] = act['point'][4]
                            win._fill.execute(win)
                        except KeyError:
                            pass


class Remove(Command):
    def __init__(self, executor=Remover()) -> None:
        self.importer = executor

    def execute(self, win, target):
        logging.debug("Delete command")
        if target == "route":
            self.importer.delete_selected_route(win=win)
        elif target == "point":
            self.importer.delete_selected_point(win)

    def cancel(self, win, name) -> None:
        key = list(name.keys())[0]
        if key == 'Polyline' or key == 'GPX':
            route = name[key]
            routes_pool.update({route.title: route})
            route.fill_route_table(win)
        if key == 'Point':
            sub = name['Point']
            route = routes_pool[sub[0]]
            route.points.insert(sub[1], sub[2])
            win._fill.execute(win)
        logging.debug("Remove Сommand Cancel")


if __name__ == "__main__":
    pass
