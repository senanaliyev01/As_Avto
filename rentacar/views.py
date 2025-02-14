from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Car
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
# Create your views here.

@login_required
class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'
    
    
@login_required
class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'
