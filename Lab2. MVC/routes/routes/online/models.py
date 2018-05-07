from django.db import models


class Route(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, default=id)
    date = models.DateField(auto_now_add=True) 
    length = models.PositiveIntegerField(default=0)

    points = None
    height = None

    class Meta:
        ordering = ["id"]

    # def get_absolute_url(self):
    #      """
    #      Returns the url to access a particular instance of Post.
    #      """
    #      return reverse('post', args=[str(self.id)])
    
    def __str__(self):
        return self.title