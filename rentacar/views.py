from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Car

# Create your views here.

class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'

class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'
