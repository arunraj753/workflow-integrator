from datetime import date, timedelta, datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse

from server.settings import logger
from utils.constants import WF_IN_PROGRESS_VALUE
from utils.utils import date_to_string, string_to_date
from wfit.models import TrelloBoard, Client, Project, Release, JobTrackerJournal, JobTracker
from wfit.tasks import run_workflow_integrator


def home(request):
    board_queryset = TrelloBoard.objects.filter(is_working_board=True, is_active=True)
    context = {"trello_boards": board_queryset}
    return render(request, "wfit/home.html", context=context)


def get_client_project_release(request, requestor):
    if requestor == "client":
        title = "Clients"
        clients = Client.objects.all()
        context = {"title": title, "records": clients, "requestor": "client"}
    elif requestor == "project":
        title = "Projects"
        projects = Project.objects.all()
        context = {"title": title, "records": projects, "requestor": "project"}
    elif requestor == "release":
        title = "Releases"
        releases = Release.objects.all()
        context = {"title": title, "records": releases, "requestor": "release"}
    elif requestor == "user":
        title = "User Completions"
        user = User.objects.first()
        user.name = "Admin"
        context = {"title": title, "records": [user], "requestor": "user"}
    else:
        messages.error(request, f"Invalid Requestor")
        return redirect("home")
    if not context["records"]:
        messages.warning(request, f"Records not found for {requestor}")
        return redirect("home")

    return render(request, "wfit/client_project_release.html", context=context)


def choose_timeframe(request, pk, requestor):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday() + 1)
    start_of_month = datetime(today.year, today.month, 1)
    today_string = date_to_string(today)
    start_of_week_string = date_to_string(start_of_week)
    start_of_month_string = date_to_string(start_of_month)
    context = {"today": today_string, "week_start": start_of_week_string, "month_start": start_of_month_string,
               "pk": pk, "requestor": requestor}
    return render(request, "wfit/timeframe.html", context=context)


def get_job_tracker_journal(request, pk, start_date, end_date, requestor):
    total_time_invested = 0
    filter_start_date = string_to_date(start_date)
    filter_end_date = string_to_date(end_date) + timedelta(days=1)

    if requestor == "client":
        client = Client.objects.filter(id=pk).first()
        title = client.name
        if not client:
            messages.error(request, f"Client not Found")
            return redirect("home")
        job_tracker_journal_objects = JobTrackerJournal.objects.filter(
            job_tracker__job_card__project__client=client,
            journal_date__gte=filter_start_date,
            journal_date__lte=filter_end_date
        )
    elif requestor == "project":
        project = Project.objects.filter(id=pk).first()
        title = project.name
        if not project:
            messages.error(request, f"Project not Found")
            return redirect("home")
        job_tracker_journal_objects = JobTrackerJournal.objects.filter(
            job_tracker__job_card__project=project,
            journal_date__gte=filter_start_date,
            journal_date__lte=filter_end_date
        )
    elif requestor == "user":
        title = "User's completions"
        job_tracker_journal_objects = JobTrackerJournal.objects.filter(
            journal_date__gte=filter_start_date,
            journal_date__lte=filter_end_date
        )
    else:
        messages.error(request, f"Invalid requestor")
        return redirect("home")

    if not job_tracker_journal_objects:
        messages.error(request, f"Job Tracker Journal is empty in between {start_date} and {end_date}")
        return redirect("home")
    for journal in job_tracker_journal_objects:
        total_time_invested += journal.time_invested
    context = {"total_time_invested": total_time_invested,
               "job_tracker_journals": job_tracker_journal_objects, "title": title,
               "start_to_end": f"{start_date} - {end_date}"}
    return render(request, 'wfit/sessions_history.html', context)


def add_job_tracker_journal_today(request):
    return redirect('create-journal' + '?date=' + date_to_string(date.today()))


def create_job_tracker_journal(request):
    date_string = request.GET.get('date')
    journal_date = string_to_date(date_string)
    if not journal_date:
        messages.error(request, "Invalid journal date")
        return redirect("home")
    if request.method == 'POST':
        try:
            job_tracker_id = request.POST.get('job_tracker_id')
            time_from_user = request.POST.get('time_from_user')
            job_tracker_obj = JobTracker.objects.get(id=job_tracker_id)
            JobTrackerJournal.objects.create(
                job_tracker=job_tracker_obj,
                journal_date=journal_date,
                time_from_user=time_from_user,
                time_invested=time_from_user,
                user_verified=True
            )
            message = f"Journal entry: {time_from_user} minutes added for {job_tracker_obj.job_card.name}"
            messages.success(request, message)
            return redirect('create-journal' + '?date=' + date_string)
        except Exception as err:
            messages.error(request, f"Journal entry failed. Reason: {err}")
            return redirect('create-journal' + '?date=' + date_string)

    job_tracker_without_journal_entry = JobTracker.objects.filter(
        being_tracked=True, job_card__trello_list__workflow_stage__gte=WF_IN_PROGRESS_VALUE).exclude(
        jobtrackerjournal__journal_date=journal_date,
        jobtrackerjournal__user_verified=True).first()

    if not job_tracker_without_journal_entry:
        messages.warning(request, f"All job trackers have journal entry on {date_string}")
        return redirect("home")

    else:
        pass
    context = {"job_name": job_tracker_without_journal_entry.job_card.name,
               "job_tracker_id": job_tracker_without_journal_entry.id}
    return render(request, 'wfit/create_journal.html', context=context)


def test(request):
    return redirect("home")


def run_wfit(request):
    try:
        logger.info("run_wfit called")
        status = run_workflow_integrator()
        if status:
            messages.info(request, f"WFIT executed successfully")
            return redirect("home")
        messages.error(request, f"WFIT execution failed.")
        return redirect("home")

    except Exception as err:
        messages.error(request, f"WFIT execution failed. Reason: {err}")
        return redirect("home")
