from django.contrib import admin

# Register your models here.

from .models import TaskList, WholeList

admin.site.register(TaskList)
admin.site.register(WholeList)
