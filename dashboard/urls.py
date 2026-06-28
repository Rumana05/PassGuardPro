from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('generator/', views.generator_view, name='generator'),
    path('activity/', views.activity_log_view, name='activity_log'),
]