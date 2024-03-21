from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("board-details/<int:trello_board_pk>", views.board_details, name="board-details"),
    path("change-workflow-stage/<int:trello_list_pk>", views.change_workflow_stage, name="change-workflow-stage"),
    path("workflow/<str:requestor>", views.get_client_project_release, name="client-project-release"),
    path("choose-timeframe/<int:pk>/<str:requestor>", views.choose_timeframe, name="choose-timeframe"),
    path("create-journal", views.create_job_tracker_journal, name="create-journal"),
    path("journal-today", views.add_job_tracker_journal_today, name="journal-today"),
    path("journal/<int:pk>/<str:start_date>/<str:end_date>/<str:requestor>",
         views.get_job_tracker_journal, name="journal"),
    path("pause-journal/<int:pk>", views.pause_journal, name="pause-journal"),
    path("never-journal/<int:pk>", views.never_journal, name="never-journal"),
    path("run-wfit", views.run_wfit, name="run-wfit"),
    path("test", views.test, name="test"),
]
