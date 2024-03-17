from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("workflow/<str:requestor>", views.get_client_project_release, name="client-project-release"),
    path("choose-timeframe/<int:pk>/<str:requestor>", views.choose_timeframe, name="choose-timeframe"),
    path("create-journal", views.create_job_tracker_journal, name="create-journal"),
    path("journal-today", views.add_job_tracker_journal_today, name="journal-today"),
    path("journal/<int:pk>/<str:start_date>/<str:end_date>/<str:requestor>",
         views.get_job_tracker_journal, name="journal"),
    path("run-wfit", views.run_wfit, name="run-wfit"),
    path("test", views.test, name="test"),
]
