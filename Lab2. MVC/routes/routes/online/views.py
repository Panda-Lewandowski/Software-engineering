from django.shortcuts import render
from django.http import JsonResponse
from polyline import encode, decode 
from .models import Route
from datetime import datetime
from math import sin, cos, acos
import json

R = 6371  # Polar radius

def index(request):
    return render(
        request,
        'index.html',

    )


def add_poly(request):
    if request.method == "POST":
        p = decode(request.POST['poly'])
        length = R * acos(sin(p[0][0]) * sin(p[-1][0]) +
                          cos(p[0][0]) * cos(p[-1][0]) *
                          cos(p[0][1] - p[-1][1]))
        
        json_points = []
        for i in range(len(p)):
            json_points.append({
                'id':i+1,
                'lat': p[i][0],
                'lon': p[i][1],
                'ele': 0
            })
            
        route = Route(title=request.POST['name'], date=datetime.now(), length=round(length, 4), points=json_points)
        if Route.objects.all().count() > 1:
            Route.objects.all().delete() #FIXME
        
        route.save()

        data = {'id':route.id, 'name':route.title, 'len':route.length, 'date':route.date}
    
        return JsonResponse(data)


def get_points(request):
    if request.method == "POST":
        route = Route.objects.filter(id__exact=request.POST['id'])[0]
        return JsonResponse({'points':route.points})


def get_ele(request):
    if request.method == "POST":
        route = Route.objects.filter(id__exact=request.POST['id'])[0]
        eles = []
        min_ele = None
        max_ele = None
        for i in range(len(route.points)):
            p = route.points[i]['ele']
            if min_ele is None or p < min_ele:
                min_ele = p
            if max_ele is None or p > max_ele:
                max_ele = p

            length = R * acos(sin(route.points[0]['lon']) * sin(route.points[i]['lon']) +
                          cos(route.points[0]['lon']) * cos(route.points[i]['lon']) *
                          cos(route.points[0]['lat'] - route.points[i]['lat']))

            eles.append({
                'id':i,
                'ele':p,
                'x':round(length, 3)
            })
        h = (min_ele + max_ele) / 10
        return JsonResponse({'min':min_ele, 'max':max_ele, 'h':h, 'eles':eles}) 


def delete_route(request):
    if request.method == "POST":
        route = Route.objects.filter(id__exact=request.POST['id'])[0]
        route.delete()
        return JsonResponse({'status':'ok'}) 

def delete_point(request):
    if request.method == "POST":
        route = Route.objects.filter(id__exact=request.POST['id_route'])[0]
        route.points.pop(int(request.POST['id_point']) - 1)
        route.save()
        return JsonResponse({'status':'ok'}) 