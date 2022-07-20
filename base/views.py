from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic import DetailView
from .models import Task, TaskList
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
class Login(LoginView):
    template_name= 'login.html'
    fields = '__all__'
    redirect_authenticated_user = True 

    def get_success_url(self):
        return reverse_lazy('list-summary')

class Register(FormView):
    form_class = UserCreationForm
    template_name = 'register.html'
    redirect_authenticated_user = True
    success_url= reverse_lazy('home-room')

    def form_valid(self,form):
        user=form.save()
        if user is not None:
            login(self.request,user)
        return super(Register,self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home-room')
        return super(Register,self).get(*args, **kwargs)
        
    
  


# class HomeRoom(LoginRequiredMixin,ListView):
#     model = Task
#     context_object_name = 'tasks'
#     template_name = 'home-room.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         print(context)
#         context['tasks'] = context['tasks'].filter(taskinfo__id=self.request.resolver_match.kwargs.get('pk'))
#         context['count'] = context['tasks'].filter(completed=False).count()
        
#         search_input = self.request.GET.get('search-area') or ''
#         if search_input:
#             context['tasks'] = context['tasks'].filter(name__icontains=search_input)
        
#         context['search_input']= search_input
        
#         return context

class HomeRoom(PermissionRequiredMixin,LoginRequiredMixin,DetailView):
    model = TaskList
    template_name = 'home-room.html'
    context_object_name = 'room'

    def get_permission_required(self):
        
        perms=[]
        tasklist = self.get_object()
        permission = Permission.objects.filter(codename=f'view_task_{tasklist.name}')
        # ct=ContentType.objects.get(id=permission.content_type)
        for perm in permission:
            applabel=perm.content_type.app_label
            perms.append(f'{applabel}.{perm.codename}')
        return perms

class TaskDetail(LoginRequiredMixin,DetailView):
    model = Task
    template_name = 'details.html'
    context_object_name = 'task'

class TaskCreate(LoginRequiredMixin,CreateView):
           
    model = Task
    fields = ['name', 'description', 'completed', 'taskinfo']
    success_url= reverse_lazy('list-summary')
    template_name = 'task_form.html'
    
    
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

   

class TaskEdit(LoginRequiredMixin,UpdateView):
    model = Task
    fields = ['name', 'description', 'completed']
    success_url= reverse_lazy('list-summary')
    template_name = 'task_form.html'

class TaskDelete(LoginRequiredMixin,DeleteView):
    model = Task
    success_url= reverse_lazy('list-summary')
    template_name = 'delete-task.html'
    context_object_name = 'task'

# class ListSummary(LoginRequiredMixin,ListView):
#     model = TaskList
#     context_object_name = 'lists'
#     template_name = 'list-summary.html'

class ListSummary(ListView):
    
    model = TaskList
    template_name = 'list-summary.html'
    context_object_name = 'rooms'
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = self.model.objects.all()
            return queryset
        
        group_names=[]
        groups= self.request.user.groups.all()
        for group in groups:
            group=str(group)
            group=group.split('_')
            group_names.append(group[0])
                          
        queryset = self.model.objects.filter(name__in=group_names)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset
    
    
       
        
    
      

class TaskListCreate(LoginRequiredMixin,CreateView):
           
    model = TaskList
    fields = ['name',]
    success_url= reverse_lazy('list-summary')
    template_name = 'tasklist_form.html'

        
    def form_valid(self,form):
        form.instance.host = self.request.user
        new_group, created = Group.objects.get_or_create(name=f'{form.instance.name}_group')
        ct = ContentType.objects.get_for_model(TaskList)
        perms_list=['add_task','change_task', 'delete_task', 'view_task']
        for perm in perms_list:
            permission = Permission.objects.create(codename=f'{perm}_{form.instance.name}',
                                   name=f'Can {perm} {form.instance.name}',
                                   content_type=ct)
            # tasklist_perm = Permission.objects.get(codename='add_task')
            new_group.permissions.add(permission)
        return super(TaskListCreate, self).form_valid(form)
    