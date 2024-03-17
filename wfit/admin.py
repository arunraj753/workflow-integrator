from django.contrib import admin

from wfit.models import (TrelloBoard, TrelloList, TrelloLabel, GlobalConfig, JobCard, Project, Client, Release,
                         JobTracker, JobTrackerJournal)

# Register your models here.
admin.site.register(TrelloBoard)
admin.site.register(TrelloList)
admin.site.register(TrelloLabel)
admin.site.register(GlobalConfig)
admin.site.register(JobCard)
admin.site.register(JobTracker)
admin.site.register(Project)
admin.site.register(Client)
admin.site.register(Release)
admin.site.register(JobTrackerJournal)
