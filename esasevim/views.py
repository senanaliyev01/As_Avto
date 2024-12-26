from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def esasevim(request):
    return render(request, 'main.html')  # main.html şablonuna baxır
