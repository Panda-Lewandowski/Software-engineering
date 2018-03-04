from PyQt5.QtWidgets import QTableWidgetItem
import gpxpy
import gpxpy.gpx
import polyline

routes_pool = []


class Routes:  # TODO приспособленец
    def __init__(self):
        pass


class RoutesCreator:  # фабрика
    @staticmethod
    def fill_route_table(route, name, win):  # TODO переделать через класс
        r = win.routes.rowCount()
        win.routes.insertRow(r)
        title = QTableWidgetItem("{0}".format(name))
        length = QTableWidgetItem("{0:.3f}".format(route.length_2d()))
        time = QTableWidgetItem("{0}".format(route.time))
        win.routes.setItem(r, 0, title)
        win.routes.setItem(r, 1, length)
        win.routes.setItem(r, 2, time)

    @staticmethod
    def create_route(source, name, win):
        if type(source) == gpxpy.gpx.GPX:
            print(name.split('.')[0])
            RoutesCreator.fill_route_table(source, name.split('.')[0], win)
            # for track in source.tracks:
            #     for segment in track.segments:
            #         for point in segment.points:
            #             print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))

        elif type(source) == 'polyline':
            pass
        else:
            print(type(source))
            raise Exception("Wrong type of source of the route! Please check it!")


