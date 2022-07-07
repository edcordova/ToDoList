from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
urlpatterns=[
    path('', views.Home.as_view(), name='home'),
    path('task/<int:pk>', views.TaskDetail.as_view(), name='task-details'),
    path('task-create/', views.TaskCreate.as_view(), name='task-create'),
    path('task-edit/<int:pk>', views.TaskEdit.as_view(), name='task-edit'),
    path('task-delete/<int:pk>', views.TaskDelete.as_view(), name='task-delete'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.Register.as_view(), name='register'),
]