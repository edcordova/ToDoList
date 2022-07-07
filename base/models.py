from django.db import models

from django.contrib.auth.models import User


# Create your models here.
class TaskList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    completed= models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['completed']



        