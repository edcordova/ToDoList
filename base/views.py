from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic import DetailView
from .models import TaskList
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import login

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
class Login(LoginView):
    template_name= 'login.html'
    fields = '__all__'
    redirect_authenticated_user = True 

    def get_success_url(self):
        return reverse_lazy('home')

class Register(FormView):
    form_class = UserCreationForm
    template_name = 'register.html'
    redirect_authenticated_user = True
    success_url= reverse_lazy('home')

    def form_valid(self,form):
        user=form.save()
        if user is not None:
            login(self.request,user)
        return super(Register,self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super(Register,self).get(*args, **kwargs)
        
    
  


class Home(LoginRequiredMixin,ListView):
    model = TaskList
    context_object_name = 'tasks'
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(completed=False).count()
        
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(name__icontains=search_input)
        
        context['search_input']= search_input
        
        return context

class TaskDetail(LoginRequiredMixin,DetailView):
    model = TaskList
    template_name = 'details.html'
    context_object_name = 'task'

class TaskCreate(LoginRequiredMixin,CreateView):
    model = TaskList
    fields = ['name', 'description', 'completed']
    success_url= reverse_lazy('home')
    template_name = 'tasklist_form.html'

    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

class TaskEdit(LoginRequiredMixin,UpdateView):
    model = TaskList
    fields = ['name', 'description', 'completed']
    success_url= reverse_lazy('home')
    template_name = 'tasklist_form.html'

class TaskDelete(LoginRequiredMixin,DeleteView):
    model = TaskList
    success_url= reverse_lazy('home')
    template_name = 'delete-task.html'
    context_object_name = 'task'


