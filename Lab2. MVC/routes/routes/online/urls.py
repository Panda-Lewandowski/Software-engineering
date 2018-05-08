from django.conf.urls import url

from . import views


urlpatterns = [
    url(r"^addpoly/$", views.add_poly),
    url(r"^getpoints/$", views.get_points),
    url(r"^getele/$", views.get_ele),
    url(r"^delroute/$", views.delete_route),
    url(r"^delpoint/$", views.delete_point),
    url(r'^$', views.index)
]