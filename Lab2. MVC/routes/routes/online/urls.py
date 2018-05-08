from django.conf.urls import url

from . import views


urlpatterns = [
    url(r"^addpoly/$", views.add_poly),
    url(r'^$', views.index)
]