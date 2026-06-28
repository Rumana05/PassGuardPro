from django.urls import path
from . import views

urlpatterns = [
    path('', views.analyzer_view, name='analyzer'),
    path('api/analyze/', views.analyze_api, name='analyze_api'),
]