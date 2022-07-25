from multiprocessing import context
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
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
    

    def get_context_data(self,*args, **kwargs):
        context = super(HomeRoom, self).get_context_data(*args,**kwargs)
        form = ParticipantsForm()
        tasklist = self.get_object()
        participants= tasklist.participants.all()
        count = tasklist.task_set.all().count()   #contar por completadas, falta un filter
        context['participants'] = participants
        context['count'] = count
        context['form'] = form
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


# class TaskDetail(PermissionRequiredMixin,DetailView):
#     model = Task
#     template_name = 'details.html'
#     context_object_name = 'task'



class TaskCreate(LoginRequiredMixin,CreateView):
           
    model = Task
    fields = ['name', 'description', 'completed', 'taskinfo']
    success_url= reverse_lazy('list-summary')
    template_name = 'task_form.html'
    context_object_name = 'task'
    

    def get_context_data(self, **kwargs):
        
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super().get_context_data(**kwargs)                
     
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

    

    def post(self, request, *args, **kwargs):
    
        form = self.get_form()
        if form.is_valid():
            
            permission=request.user.get_all_permissions()
            tasklist_name=form.cleaned_data.get('taskinfo')
            app_label = self.model._meta.app_label
            permission_required = f'{app_label}.add_task_{tasklist_name}'
            
            
            if permission_required in permission:
                
                           
                return self.form_valid(form)
            
            else:
                messages.success(request, 'You dont have permission to post on this Task List')
        
                return HttpResponseRedirect(self.request.path_info)
        

   

class TaskEdit(PermissionRequiredMixin,UpdateView):
    model = Task
    fields = ['name', 'description', 'completed']
    success_url= reverse_lazy('list-summary')
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

class TaskDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model = Task
    success_url= reverse_lazy('list-summary')
    template_name = 'delete-task.html'
    context_object_name = 'task'

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
    
    # def post(self, request, *args, **kwargs):
    
    #     form = self.get_form()
    #     if form.is_valid and request.user.is_superuser:
                                                      
    #         return self.form_valid(form)
    #     else:
    #         messages.success(request, 'You dont have permission create a Task List')
        
    #         return HttpResponseRedirect(self.request.path_info)

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
            # tasklist_perm = Permission.objects.get(codename='add_task')
            new_group.permissions.add(permission)
        return super(TaskListCreate, self).form_valid(form)
    
