from django.db import models
from django.contrib.postgres.fields import JSONField
import datetime
import reversion
from routes import settings

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

@reversion.register()
class OperationStack(models.Model):
    op = models.CharField(max_length=50, default="edit")
    pk_route = models.PositiveIntegerField(default=0)
    num_version = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):        
        super().save(*args, **kwargs)  # Call the "real" save() method.
        settings.INDEX += 1 

    def __str__(self):
        return str(self.op) + "#" + str(self.id) +" on " + str(self.pk_route) + " route (v."+ str(self.num_version) + ")"


