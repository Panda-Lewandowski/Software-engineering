from django.shortcuts import render
from django.http import JsonResponse
from polyline import encode, decode 
from datetime import datetime
from math import sin, cos, acos
import json
import os
import gpxpy
import gpxpy.gpx
import reversion
from reversion.models import Version
from .models import Route, OperationStack 
from routes import settings

R = 6371  # Polar radius


def index(request):
    routes = Route.objects.all()
    data = '['
    for r in routes:
        data += json.dumps({'id':r.id,
                            'name':r.title, 
                            'len':r.length, 
                            'date':datetime.strftime(r.date, "%Y-%m-%d")}) + ','

    if data != '[':
        data = data[:-1] + ']'
    else:
        data += ']' 
    return render(
        request,
        'index.html',
        {"json_data":data}

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

        with reversion.create_revision(): 
            route = Route(title=request.POST['name'], date=datetime.now().date(), 
                        length=round(length, 4), points=json_points)
            
            route.save()

            op = OperationStack(op='add_poly', pk_route=route.id, num_version=0)
            op.save()



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
            if p is not None:
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
        if min_ele is not None and max_ele is not None:
            h = (min_ele + max_ele) / 10
        else:
            h = 0

        return JsonResponse({'min':min_ele, 'max':max_ele, 'h':h, 'eles':eles}) 


def delete_route(request):
    if request.method == "POST":
        route = Route.objects.filter(id__exact=request.POST['id'])[0]
        ver = Version.objects.get_for_object(route)
        op = OperationStack(op='del_route', pk_route=route.id, num_version=len(ver)+1)
        op.save()
        route.delete()
        
        return JsonResponse({'status':'ok'}) 


def delete_point(request):
    if request.method == "POST":
        with reversion.create_revision(): 
            route = Route.objects.filter(id__exact=request.POST['id_route'])[0]
            route.points.pop(int(request.POST['id_point']) - 1)
            route.save()
            ver = Version.objects.get_for_object(route)
            op = OperationStack(op='del_point', pk_route=route.id, num_version=len(ver)+1)
            op.save()
        return JsonResponse({'status':'ok'}) 


def edit_route(request):
    if request.method == "POST":
        with reversion.create_revision(): 
            route = Route.objects.filter(id__exact=request.POST['id'])[0]
            qual = request.POST['qual']
            new_value = request.POST['val']

            if qual == 'name':
                route.title = new_value
            elif qual == 'date':
                route.date = datetime.strptime(new_value, "%Y-%m-%d").date()

            ver = Version.objects.get_for_object(route)
            op = OperationStack(op='edit_route', pk_route=route.id, num_version=len(ver)+1)
            op.save()
            route.save()
        return JsonResponse({'status':'ok'}) 


def edit_point(request): #FIXME
    if request.method == "POST":
        with reversion.create_revision(): 
            route = Route.objects.filter(id__exact=request.POST['id_route'])[0]
            qual = request.POST['qual']
            new_value = float(request.POST['val'])
            j = int(request.POST['id']) - 1

            val = None

            if qual == 'lon':
                route.points[j]['lon'] = new_value
                route.save()
                length = R * acos(sin(route.points[0]['lon']) * sin(route.points[-1]['lon']) +
                            cos(route.points[0]['lon']) * cos(route.points[-1]['lon']) *
                            cos(route.points[0]['lat'] - route.points[-1]['lat']))

                val = round(length, 4)
            elif qual == 'lat':
                route.points[j]['lon'] = new_value
                route.save()
                length = R * acos(sin(route.points[0]['lon']) * sin(route.points[-1]['lon']) +
                            cos(route.points[0]['lon']) * cos(route.points[-1]['lon']) *
                            cos(route.points[0]['lat'] - route.points[-1]['lat']))
                val = round(length, 4)
            elif qual == 'ele':
                route.points[j]['ele'] = new_value
                route.save()
                eles = []
                min_ele = None
                max_ele = None
                for i in range(len(route.points)):
                    p = route.points[i]['ele']
                    if p is not None:
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
                if min_ele is not None and max_ele is not None:
                    h = (min_ele + max_ele) / 10

            ver = Version.objects.get_for_object(route)
            op = OperationStack(op='edit_point', pk_route=route.id, num_version=len(ver)+1)
            op.save()
                
            return JsonResponse({'val': eles, 'min':min_ele, 'max':max_ele, 'h':h})
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
                        json_points.append({
                            'id':i+1,
                            'lat': p.latitude,
                            'lon': p.longitude,
                            'ele': p.elevation
                        })
                        
                        
                        i += 1

            with reversion.create_revision():     
                route = Route(title=file.name.split(".")[:-1], date=datetime.now().date(), 
                        length=gpx.length_2d(), points=json_points)
            
                route.save()

                op = OperationStack(op='add_gpx', pk_route=route.id, num_version=0)
                op.save()
            return JsonResponse({
                                    "status":"server", 
                                    'id':route.id, 
                                    'name':route.title, 
                                    'len':round(route.length, 4), 
                                    'date':route.date
                                }) 

        os.remove('/tmp/' + file.name)

    return JsonResponse({"status":"server"}) 


def delete_all(request):
    count = Route.objects.all().delete()
    return JsonResponse({"status":"server", "n":count[0]}) 


def undo(request):
    if settings.INDEX > 0: 
        try:
            op = OperationStack.objects.get(id__exact=settings.INDEX)
            settings.INDEX -= 1
            try:
                route = Route.objects.get(id__exact=op.pk_route)
            except Route.DoesNotExist:
                    if op.op != "del_route":
                        return JsonResponse({"status":"error"})
                    else: 
                        deleted = Version.objects.get_deleted(Route)
                        deleted.get_for_object_reference(Route, op.pk_route)[0].revert()
                        route = Route.objects.get(id__exact=op.pk_route)
                        return JsonResponse({"status":"server", "act": "add",
                                             "val": {'id':route.id, 'name':route.title, 'len':route.length, 'date':route.date}}) 
            if op.op == "add_poly" or op.op == "add_gpx":
                route.delete()
                return JsonResponse({"status":"server", "act": "remove", "val": op.pk_route}) 
            if op.op == "edit_route":
                versions = Version.objects.get_for_object(route)
                versions[len(versions) - op.num_version + 1].revision.revert()
                route.refresh_from_db()
                return JsonResponse({"status":"server", "act": "edit_route", 
                            "val": {'id':route.id, 'name':route.title, 'len':route.length, 'date':route.date}}) 
            if op.op == "edit_point" or op.op == "del_point":
                versions = Version.objects.get_for_object(route)
                versions[len(versions) - op.num_version + 1].revision.revert()
                route.refresh_from_db()
                return JsonResponse({"status":"server", "act": "edit_point", 
                            "val": {"id":route.id, "points":route.points}}) 

            # del_route
            return JsonResponse({"status":"uknown operation"}) 
            
        except OperationStack.DoesNotExist:
            return JsonResponse({"status":"error"})
           
        
    else: 
        return JsonResponse({"status":"nothing"})
