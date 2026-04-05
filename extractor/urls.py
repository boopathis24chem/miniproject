from django.urls import path
from . import views

urlpatterns = [
    path("", views.calculate, name="calculate"),
    path("rpm_graph/", views.rpm_graph, name="rpm_graph"),
    path("flow_graph/", views.flow_graph, name="flow_graph"),
]