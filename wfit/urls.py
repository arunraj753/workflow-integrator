from django.urls import path
from . import views

urlpatterns = [
    # path("", views.home, name="home"),
    path("run-wfit", views.run_wfit, name="run-wfit"),
    path("test", views.test, name="test"),
]
