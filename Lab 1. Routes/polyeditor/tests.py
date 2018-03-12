from polyline import decode, encode
import unittest
import logging

test_points = [[(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)],
               [(55.75841, 37.59826), (55.76382, 37.61508), (55.75803, 37.63362), (55.74721, 37.63808)],
               [(41.37339, 2.17652), (41.38074, 2.18598), (41.38525, 2.18087), (41.39048, 2.16991)],
               [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
               [(-1, -2), (-3, -4), (-5, -6)]]

test_polyline = ['_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'aiisIclndFy`@chBdc@{rBrbA{Z', 'uvo{FgbhL}l@cz@e[|^u_@ncA',
                 '??????????', '~hbE~reK~reK~reK~reK~reK']


class ConvertToPolylineTestCase(unittest.TestCase):
    def test_convert(self):
        for i in range(len(test_points)):
            self.assertEqual(encode(test_points[i]), test_polyline[i])


class DeleteRouteTestCase(unittest.TestCase):
    pass


class ImportPolylineTestCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s] %(message)s',
                        level=logging.DEBUG, filename="test.log")

    unittest.main()
