from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculate),
]

urlpatterns = [
    path('', views.calculate),
    path('graph/', views.graph),
]