from multiprocessing import context
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic import DetailView
from .models import Task, TaskList
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.contrib.auth.forms import UserCreationForm
from .forms import ParticipantsForm

from django.contrib import messages

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
        

  



class HomeRoom(PermissionRequiredMixin,LoginRequiredMixin,DetailView):
    model = TaskList
    template_name = 'home-room.html'
    context_object_name = 'room'
    

    def get_context_data(self,*args, **kwargs):
        context = super(HomeRoom, self).get_context_data(*args,**kwargs)
        form = ParticipantsForm()
        tasklist = self.get_object()
        participants= tasklist.participants.all()
        count = tasklist.task_set.filter(completed=False).count()  
        context['participants'] = participants
        context['count'] = count
        context['form'] = form
        search_input = self.request.GET.get('search-area') or ''
        rooms=tasklist.task_set.all()
        if search_input != '':
            rooms = rooms.filter(
                name__icontains=search_input)
            
        context['rooms']=rooms
            
               
        return context


    def get_permission_required(self):
        
        perms=[]
        tasklist = self.get_object()
        permission = Permission.objects.filter(codename=f'view_task_{tasklist.name}')
          
        for perm in permission:
            applabel=perm.content_type.app_label
            perms.append(f'{applabel}.{perm.codename}')
        return perms


    def post(self, request, *args, **kwargs):
        tasklist = self.get_object()
        
        group=Group.objects.get(name=f'{tasklist}_group')     
        users = request.POST.get('users')
        group.user_set.add(users)
        tasklist.participants.add(users)
        messages.success(request, 'Users add to Task List')
        
        return HttpResponseRedirect(self.request.path_info)



class TaskCreate(LoginRequiredMixin,CreateView):
           
    model = Task
    fields = ['name', 'description', 'completed']
    success_url= reverse_lazy('list-summary')
    template_name = 'task_form.html'
    context_object_name = 'task'
     
    def form_valid(self,form,**kwargs):
        form.instance.user = self.request.user
        tasklist_id=kwargs.get('pk')
        form.instance.taskinfo = TaskList.objects.get(id=tasklist_id)
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url(**kwargs))

    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        
        if form.is_valid():
            
            permission=request.user.get_all_permissions()
            tasklist_id=kwargs.get('pk')
            tasklist_name=TaskList.objects.get(id=tasklist_id).name
            
            app_label = self.model._meta.app_label
            permission_required = f'{app_label}.add_task_{tasklist_name}'
            
            
            if permission_required in permission:        
                return self.form_valid(form,**kwargs)
            
            else:
                messages.success(request, 'You dont have permission to post on this Task List')
                return HttpResponseRedirect(self.request.path_info)

    def get_success_url(self, **kwargs): 
        tasklist_id=kwargs.get('pk')
        return reverse_lazy('home-room', kwargs={'pk':tasklist_id})

    
class TaskEdit(PermissionRequiredMixin,UpdateView):
    model = Task
    fields = ['name', 'description', 'completed']
    template_name = 'task_form.html'
    context_object_name = 'task'

    def get_permission_required(self):
    
        perms=[]
        task = self.get_object()
        tasklist_name=task.taskinfo.name
        permission = Permission.objects.filter(codename=f'view_task_{tasklist_name}')
                
        for perm in permission:
            applabel=perm.content_type.app_label
            perms.append(f'{applabel}.{perm.codename}')
            
        return perms

    def get_success_url(self, **kwargs): 
        task=self.get_object()  
        tasklist=task.taskinfo.id   
                       
        return reverse_lazy('home-room', kwargs = {'pk': tasklist})

class TaskDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Task
    
    template_name = 'delete-task.html'
    context_object_name = 'task'

    def get_success_url(self, **kwargs): 
        task=self.get_object()  
        tasklist=task.taskinfo.id   
        
        return reverse_lazy('home-room', kwargs = {'pk': tasklist})
        

    def get_permission_required(self):

        perms=[]
        task = self.get_object()
        tasklist_name=task.taskinfo.name
        permission = Permission.objects.filter(codename=f'delete_task_{tasklist_name}')
                
        for perm in permission:
            applabel=perm.content_type.app_label
            perms.append(f'{applabel}.{perm.codename}')
            
        return perms



class ListSummary(LoginRequiredMixin, ListView):
    
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
    
    def get(self, request, *args, **kwargs):
        self.object = None
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)    
        else:
            messages.success(request, 'You dont have permission create a Task List')
        
            return HttpResponseRedirect(reverse_lazy('list-summary'))

            
    def form_valid(self,form):
        form.instance.host = self.request.user
        new_group, created = Group.objects.get_or_create(name=f'{form.instance.name}_group')
        ct = ContentType.objects.get_for_model(TaskList)
        perms_list=['add_task','change_task', 'delete_task', 'view_task']
        for perm in perms_list:
            permission = Permission.objects.create(codename=f'{perm}_{form.instance.name}',
                                   name=f'Can {perm} {form.instance.name}',
                                   content_type=ct)
            
            new_group.permissions.add(permission)
        return super(TaskListCreate, self).form_valid(form)
    
class TaskListDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model =  TaskList
    template_name = 'tasklist-delete.html'
    context_object_name = 'tasklist'
    success_url= reverse_lazy('list-summary')

    def get_permission_required(self):

        perms=[]
        tasklist = self.get_object()
        
        permission = Permission.objects.filter(codename=f'delete_task_{tasklist.name}')
                
        for perm in permission:
            applabel=perm.content_type.app_label
            perms.append(f'{applabel}.{perm.codename}')
            
        return perms

    def form_valid(self, form):
        success_url = self.get_success_url()
        group = Group.objects.get(name=f'{self.object.name}_group')
        group.permissions.all().delete()
        group.delete()
        
        self.object.delete()
        return HttpResponseRedirect(success_url)

    
