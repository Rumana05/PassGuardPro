from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

@login_required
def generator_view(request):
    return render(request, 'dashboard/generator.html')

@login_required
def activity_log_view(request):
    return render(request, 'dashboard/activity_log.html')