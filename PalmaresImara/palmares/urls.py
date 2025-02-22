from django.urls import path
from . import views


urlpatterns = [
    path('', views.recherche, name='recherche'),
    path('login/', views.login_view, name='login'),  
    path('ajax/sections-classes/', views.charger_sections_classes, name='charger_sections_classes'),
]