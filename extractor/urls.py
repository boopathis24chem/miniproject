
from django.urls import path
from . import views

urlpatterns = [
    path("", views.calculate),
    path("rpm_graph/", views.rpm_graph),
    path("flow_graph/", views.flow_graph),
    path("water_graph/", views.water_graph),
    path("acetone_graph/", views.acetone_graph),
]