from django.test import TestCase
from polyline import decode, encode
from django.core.urlresolvers import reverse
import json
from datetime import datetime
from .models import Route
from waffle.testutils import override_switch
import waffle


class ConvertToPolylineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_points = [[(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)],
               [(55.75841, 37.59826), (55.76382, 37.61508), (55.75803, 37.63362), (55.74721, 37.63808)],
               [(41.37339, 2.17652), (41.38074, 2.18598), (41.38525, 2.18087), (41.39048, 2.16991)],
               [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
               [(-1, -2), (-3, -4), (-5, -6)]]

        cls.test_polyline = ['_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'aiisIclndFy`@chBdc@{rBrbA{Z', 'uvo{FgbhL}l@cz@e[|^u_@ncA',
                 '??????????', '~hbE~reK~reK~reK~reK~reK']
    def test_convert(self):
        for i in range(len(self.test_points)):
            self.assertEqual(encode(self.test_points[i]), self.test_polyline[i])


class AddPolyTests(TestCase):
    def test_return_value(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data['name'], 'test')
        self.assertEqual(data['date'], str(datetime.now().date()))

    def test_exist_in_db(self):
        try:
            response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
            self.assertEqual(response.status_code, 200)
            route = Route.objects.get(title='test')
        except Route.DoesNotExist:
            self.fail("Test route does not exist")

    @override_switch('ele-switch', active=True)
    def test_points(self):
        assert waffle.switch_is_active('ele-switch')
        try:
            response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
            self.assertEqual(response.status_code, 200)
            route = Route.objects.get(title='test')
            self.assertEqual(route.points, [{'id': 1, 'ele': 0, 'lat': 38.5, 'lon': -120.2}, 
                                                {'id': 2, 'ele': 0, 'lat': 40.7, 'lon': -120.95}, 
                                                {'id': 3, 'ele': 0, 'lat': 43.252, 'lon': -126.453}])
        except Route.DoesNotExist:
            self.fail("Test route does not exist")         


class GetPointsTests(TestCase):
    @override_switch('ele-switch', active=True)
    def test_get_points(self):   
        assert waffle.switch_is_active('ele-switch')
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('getpoints'), data={'id':last[id].id})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'points': [{'id': 1, 'ele': 0, 'lat': 38.5, 'lon': -120.2}, 
                                           {'id': 2, 'ele': 0, 'lat': 40.7, 'lon': -120.95}, 
                                           {'id': 3, 'ele': 0, 'lat': 43.252, 'lon': -126.453}]})


class GetEleTests(TestCase):
    @override_switch('ele-switch', active=True)
    def test_get_ele_empty(self):
        assert waffle.switch_is_active('ele-switch')
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('getele'), data={'id': last[id].id})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'min': 0, 'max': 0, 'h': 0.0, 
                                'eles': [{'id': 0, 'ele': 0, 'x': 0.0}, 
                                         {'id': 1, 'ele': 0, 'x': 4791.58}, 
                                         {'id': 2, 'ele': 0, 'x': 6389.96}]})

    @override_switch('ele-switch', active=True)
    def test_get_ele_not_empty(self):
        assert waffle.switch_is_active('ele-switch')
        pass


class DelRouteTest(TestCase):
    def test_exist_route(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('delroute'), data={'id': last[id].id})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'ok'})
        try:
            route = Route.objects.get(title__exact='test')
            self.fail()
        except Route.DoesNotExist:
            pass

    def test_not_exist_route(self):
        response = self.client.post(reverse('delroute'), data={'id': -1})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})


class DelPointTest(TestCase):
    @override_switch('ele-switch', active=True)
    def test_exist_point(self):
        assert waffle.switch_is_active('ele-switch')
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('delpoint'), data={'id_route': last[id].id, 'id_point': 1})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'ok'})
        route = Route.objects.get(title='test')
        self.assertEqual(route.points, [{'id': 2, 'ele': 0, 'lat': 40.7, 'lon': -120.95}, 
                                            {'id': 3, 'ele': 0, 'lat': 43.252, 'lon': -126.453}])

    @override_switch('ele-switch', active=True)
    def test_not_exist_point(self):
        assert waffle.switch_is_active('ele-switch')
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('delpoint'), data={'id_route': last[id].id, 'id_point': -1})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})
        route = Route.objects.get(title='test')
        self.assertEqual(route.points, [{'id': 1, 'ele': 0, 'lat': 38.5, 'lon': -120.2}, 
                                           {'id': 2, 'ele': 0, 'lat': 40.7, 'lon': -120.95}, 
                                           {'id': 3, 'ele': 0, 'lat': 43.252, 'lon': -126.453}])

 
class EditRouteTest(TestCase):
    def test_valid_title(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editroute'), data={'id': last[id].id, 'qual': 'name', 'val': 'supertest'})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'ok'})
        route = Route.objects.get(id=last[id].id)
        self.assertEqual(route.title, 'supertest')

    def test_not_valid_title(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editroute'), data={'id': last[id].id, 'qual': 'name', 'val': -1})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'ok'})
        route = Route.objects.get(id=last[id].id)
        self.assertEqual(route.title, '-1')

    def test_valid_data(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editroute'), data={'id': last[id].id, 'qual': 'date', 'val': str(datetime.now().date())})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'ok'})
        route = Route.objects.get(id=last[id].id)
        self.assertEqual(route.date, datetime.now().date())

    def test_not_valid_data(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editroute'), data={'id': last[id].id, 'qual': 'date', 'val': -1})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'invalid'})
        route = Route.objects.get(id=last[id].id)
        self.assertEqual(route.date, datetime.now().date())


class EditPointTest(TestCase):
    def test_valid_lat_lon(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'lon', 'val': 32})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status': 'ok', 'val':12410})
        route = Route.objects.get(id=last[id].id)
        self.assertEqual(route.points[0]['lon'], 32)
        self.assertEqual(route.length, 12410)

    @override_switch('ele-switch', active=True)
    def test_valid_ele(self):
        assert waffle.switch_is_active('ele-switch')
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'ele', 'val': 32})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status': 'ok', 'val': [{'id': 0, 'ele': 32.0, 'x': 0.0}, 
                                        {'id': 1, 'ele': 0, 'x': 4791.58}, 
                                        {'id': 2, 'ele': 0, 'x': 6389.96}], 
                                        'min': 0, 'max':32.0, 'h': 3.2})
        route = Route.objects.get(id=last[id].id)
        self.assertEqual(route.points[0]['ele'], 32)

    def test_not_valid_char_lon_lat(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'lon', 'val': 'lon'})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})
        route = Route.objects.get(id=last[id].id)
        self.assertEqual(route.points[0]['lon'], -120.2)
        self.assertEqual(route.length, 9757)

    @override_switch('ele-switch', active=True)
    def test_not_valid_char_ele(self):
        assert waffle.switch_is_active('ele-switch')
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'ele', 'val': 'ele'})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})
        route = Route.objects.get(id=last[id].id)
        self.assertEqual(route.points[0]['ele'], 0)

    def test_not_valid_lon_max(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'lon', 'val': 200})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})

    def test_not_valid_lon_min(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'lon', 'val': -200})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})

    def test_not_valid_lat_max(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'lat', 'val': 200})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})

    def test_not_valid_lat_min(self):
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'lat', 'val': -200})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})

    @override_switch('ele-switch', active=True)
    def test_not_valid_ele_max(self):
        assert waffle.switch_is_active('ele-switch')
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'ele', 'val': 12_000})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})

    @override_switch('ele-switch', active=True)
    def test_not_valid_ele_min(self):
        assert waffle.switch_is_active('ele-switch')
        response = self.client.post(reverse('addpoly'), data={'poly':'_p~iF~ps|U_ulLnnqC_mqNvxq`@', 'name':'test'})
        self.assertEqual(response.status_code, 200)
        last = Route.objects.all()
        id = len(last) - 1
        response = self.client.post(reverse('editpoint'), data={'id': 1, 'id_route': last[id].id, 'qual': 'ele', 'val': -12_000})
        self.assertEqual(response.status_code, 200)
        data = response.content.decode('utf8').replace("'", '"')
        data = json.loads(data)
        self.assertEqual(data, {'status':'error'})


class UploadTests(TestCase):
    def test_return_value(self):
        pass
    
    def test_exist_in_db(self):
        pass


class UndoTests(TestCase):
    pass

class RedoTests(TestCase):
    pass