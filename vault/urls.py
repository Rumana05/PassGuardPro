from django.urls import path
from . import views

urlpatterns = [
    path('', views.vault_view, name='vault'),
    path('add/', views.add_entry, name='add_entry'),
    path('delete/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    path('favourite/<int:entry_id>/', views.toggle_favourite, name='toggle_favourite'),
    path('get-password/<int:entry_id>/', views.get_password, name='get_password'),
]