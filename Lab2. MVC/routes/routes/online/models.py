from django.db import models
from django.contrib.postgres.fields import JSONField
import datetime
import reversion

@reversion.register()
class Route(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, default=id)
    date = models.DateField(default=datetime.date.today) 
    length = models.PositiveIntegerField(default=0)

    points = JSONField(default=[
                                {   
                                    'id':1,
                                    'lat':38.5, 
                                    'lon':-120.2,
                                    'ele':0
                                },
                                {   
                                    'id':2,
                                    'lat':40.7, 
                                    'lon':-120.95,
                                    'ele':0
                                }, 
                                {
                                    'id':3,
                                    'lat':43.252, 
                                    'lon':-126.453,
                                    'ele':0
                                }
    ])

    
    class Meta:
        ordering = ["id"]

    
    def __str__(self):
        return self.title

    def get_eles(self):
        pass