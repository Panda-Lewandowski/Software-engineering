from django.shortcuts import render
from django.http import JsonResponse
from polyline import encode, decode 
from .models import Route
from datetime import datetime
from math import sin, cos, acos
import json

R = 6371  # Polar radius

def index(request):
    data = {'id':1, 'name':"bla", 'len':10, 'date':'10.07.98'}
    return render(
        request,
        'index.html',
        { "json_data": json.dumps(data) }

    )


def add_poly(request):
    if request.method == "POST":
        p = decode(request.POST['poly'])
        length = R * acos(sin(p[0][0]) * sin(p[-1][0]) +
                          cos(p[0][0]) * cos(p[-1][0]) *
                          cos(p[0][1] - p[-1][1]))
        route = Route(title=request.POST['name'], date=datetime.now(), length=round(length, 4))
        route.points = p

        route.save()
    
        Route.objects.all().delete()

        data = {'id':route.id, 'name':route.title, 'len':route.length, 'date':route.date}
    
    return JsonResponse(data)