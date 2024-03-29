from django.db import models
from django.utils import timezone
from django.utils.timezone import now

from utils.constants import WORKFLOW_STAGE_CHOICES


class GlobalConfig(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "global_config"


# Create your models here.
class IntegrationStatus(models.Model):
    app_name = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=50)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    metadata = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.status


class TrelloBoard(models.Model):
    trello_board_id = models.CharField(max_length=100, unique=True)
    trello_board_name = models.CharField(max_length=100)
    is_working_board = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.trello_board_name

    class Meta:
        db_table = "trello_board"


class TrelloList(models.Model):
    trello_list_id = models.CharField(max_length=100, unique=True)
    trello_list_name = models.CharField(max_length=100)
    board = models.ForeignKey(TrelloBoard, on_delete=models.CASCADE)
    workflow_stage = models.IntegerField(choices=WORKFLOW_STAGE_CHOICES, default=0)
    user_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.trello_list_name} --> {self.board}"

    class Meta:
        db_table = "trello_list"
        unique_together = ["trello_list_name", "board"]


class TrelloLabel(models.Model):
    trello_label_id = models.CharField(max_length=200, unique=True)
    trello_label_name = models.CharField(max_length=100)
    trello_label_color = models.CharField(max_length=100)
    trello_board_id = models.CharField(max_length=200)
    board = models.ForeignKey(TrelloBoard, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.trello_label_name}|{self.trello_label_color}| {self.board}"

    class Meta:
        db_table = "trello_label"
        unique_together = ["trello_label_name", "trello_label_color", "board"]


class Client(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "client"


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    label_name = models.CharField(max_length=50, unique=True)
    planned_start = models.DateField(null=True, blank=True)
    planned_finish = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    actual_finish = models.DateField(null=True, blank=True)
    current_due = models.DateField(null=True, blank=True)
    time_invested = models.IntegerField(null=True, blank=True)
    time_unit = models.CharField(max_length=50, default="minutes", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "project"


class Release(models.Model):
    name = models.CharField(max_length=255, unique=True)
    planned_start = models.DateField(null=True, blank=True)
    planned_finish = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    actual_finish = models.DateField(null=True, blank=True)
    current_due = models.DateField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    time_invested = models.IntegerField(null=True, blank=True)
    time_unit = models.CharField(max_length=50, default="minutes", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "release"


class JobCard(models.Model):
    trello_card_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=300)
    trello_board = models.ForeignKey(TrelloBoard, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.DO_NOTHING, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    is_collaborator = models.BooleanField(default=False)
    short_url = models.CharField(max_length=100, unique=True)
    id_short = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "job_card"


class JobTracker(models.Model):
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE)
    trello_list = models.ForeignKey(TrelloList, on_delete=models.CASCADE)
    release = models.ForeignKey(Release, on_delete=models.DO_NOTHING, null=True, blank=True)
    planned_start = models.DateField(null=True, blank=True)
    planned_finish = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    actual_finish = models.DateField(null=True, blank=True)
    current_due = models.DateField(null=True, blank=True)
    time_invested = models.IntegerField(null=True, blank=True)
    time_unit = models.CharField(max_length=50, default="minutes", null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    being_tracked = models.BooleanField(default=True)
    track_start_date = models.DateField(default=timezone.now)
    track_end_date = models.DateField(blank=True, null=True)
    pause_journal = models.BooleanField(default=False)
    never_journal = models.BooleanField(default=False)

    class Meta:
        db_table = "job_tracker"

    def __str__(self):
        return self.job_card.name


class JobTrackerJournal(models.Model):
    job_tracker = models.ForeignKey(JobTracker, on_delete=models.CASCADE)
    journal_date = models.DateField(blank=True, null=True)
    time_from_user = models.IntegerField(default=0)
    time_from_sessions = models.IntegerField(default=0)
    time_invested = models.IntegerField(default=0)
    time_unit = models.CharField(max_length=50, default="minutes")
    user_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "job_tracker_journal"
        unique_together = ('job_tracker', 'journal_date')

    def __str__(self):
        return f"{self.job_tracker.job_card.name} -- {self.journal_date}"


class Session(models.Model):
    job_tracker = models.ForeignKey(JobTracker, on_delete=models.DO_NOTHING)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True, blank=True)
    time_invested = models.IntegerField(null=True, blank=True, default=0)
    time_unit = models.CharField(max_length=50, default="minutes")
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = "session"

    def __str__(self):
        return f"{self.job_tracker.job_card.name} -- {self.start_time}"