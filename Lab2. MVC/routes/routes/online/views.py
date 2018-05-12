from django.shortcuts import render
from django.http import JsonResponse
from polyline import encode, decode 
from .models import Route
from datetime import datetime
from math import sin, cos, acos
import json
import os
import gpxpy
import gpxpy.gpx

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
            
        route = Route(title=request.POST['name'], date=datetime.now().date(), 
                      length=round(length, 4), points=json_points)
        if Route.objects.all().count() > 1:
            Route.objects.all().delete() # FIXME
        
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
        h = (min_ele + max_ele) / len(eles)
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


def edit_route(request):
    if request.method == "POST":
        route = Route.objects.filter(id__exact=request.POST['id'])[0]
        qual = request.POST['qual']
        new_value = request.POST['val']

        if qual == 'name':
            route.title = new_value
        elif qual == 'date':
            route.date = datetime.strptime(new_value, "%Y-%m-%d").date()

        route.save()
        return JsonResponse({'status':'ok'}) 


def edit_point(request):
    if request.method == "POST":
        route = Route.objects.filter(id__exact=request.POST['id_route'])[0]
        qual = request.POST['qual']
        new_value = float(request.POST['val'])
        j = int(request.POST['id']) - 1

        val = None

        if qual == 'lon':
            route.points[j]['lon'] = new_value
            length = R * acos(sin(route.points[0]['lon']) * sin(route.points[-1]['lon']) +
                          cos(route.points[0]['lon']) * cos(route.points[-1]['lon']) *
                          cos(route.points[0]['lat'] - route.points[-1]['lat']))

            val = round(length, 4)
        elif qual == 'lat':
            route.points[j]['lon'] = new_value
            length = R * acos(sin(route.points[0]['lon']) * sin(route.points[-1]['lon']) +
                          cos(route.points[0]['lon']) * cos(route.points[-1]['lon']) *
                          cos(route.points[0]['lat'] - route.points[-1]['lat']))
            val = round(length, 4)
        elif qual == 'ele':
            route.points[j]['ele'] = new_value
            eles = []
            for i in range(len(route.points)):
                p = route.points[i]['ele']
                length = R * acos(sin(route.points[0]['lon']) * sin(route.points[i]['lon']) +
                          cos(route.points[0]['lon']) * cos(route.points[i]['lon']) *
                          cos(route.points[0]['lat'] - route.points[i]['lat']))

                eles.append({
                    'id':i,
                    'ele':p,
                    'x':round(length, 3)
                })

            val = eles
        return JsonResponse({'val': val}) 


def upload(request):
    if request.method == 'POST' and request.FILES['upload']:
        file = request.FILES['upload']

        if file.name.split(".")[-1] != 'gpx':
            return JsonResponse({"status":"error"}) 

        with open('/tmp/' + file.name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        with open('/tmp/' + file.name, 'r') as destination:
            gpx = gpxpy.parse(destination)

            json_points = []
            i = 0
            for track in gpx.tracks:
                for segment in track.segments:
                    for p in segment.points:
                        if p.elevation is not None:
                            json_points.append({
                                'id':i+1,
                                'lat': p.latitude,
                                'lon': p.longitude,
                                'ele': p.elevation
                            })
                        else:
                            json_points.append({
                                'id':i+1,
                                'lat': p.latitude,
                                'lon': p.longitude,
                                'ele': 0
                            })
                        
                        i += 1

                
            route = Route(title=file.name.split(".")[:-1], date=datetime.now().date(), 
                      length=gpx.length_2d(), points=json_points)

            if Route.objects.all().count() > 1:
                Route.objects.all().delete() # FIXME
        
            route.save()
            return JsonResponse({
                                    "status":"server", 
                                    'id':route.id, 
                                    'name':route.title, 
                                    'len':round(route.length, 4), 
                                    'date':route.date
                                }) 

        os.remove('/tmp/' + file.name)

    return JsonResponse({"status":"server"}) 
