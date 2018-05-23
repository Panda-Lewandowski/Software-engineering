from django.conf.urls import url

from . import views


urlpatterns = [
    url(r"^addpoly/$", views.add_poly, name="addpoly"),
    url(r"^getpoints/$", views.get_points, name="getpoints"),
    url(r"^getele/$", views.get_ele, name="getele"),
    url(r"^delroute/$", views.delete_route, name="delroute"),
    url(r"^delpoint/$", views.delete_point, name="delpoint"),
    url(r"^editroute/$", views.edit_route, name="editroute"),
    url(r"^editpoint/$", views.edit_point, name="editpoint"),
    url(r"^upload/$", views.upload, name="upload"),
    url(r"^deleteall/$", views.delete_all, name="deleteall"),
    url(r"^undo/$", views.undo, name="undo"),
    url(r"^redo/$", views.redo, name="redo"),
    url(r'^$', views.index, name="index")
]