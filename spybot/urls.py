from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('live/', views.live, name='live')
    path('helloworld/', views.index, name='index'),
    path('', views.home, name='home'),
]

