from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Car
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
# Create your views here.

class CarListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'
    
    
class CarDetailView(LoginRequiredMixin, DetailView):
    model = Car
    template_name = 'car_detail.html'
