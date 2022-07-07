from django.contrib import admin

# Register your models here.

from .models import TaskList

admin.site.register(TaskList)
