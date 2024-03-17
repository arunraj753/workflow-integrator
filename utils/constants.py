from datetime import timedelta

SYNC_TRELLO_BOARDS = "SYNC_TRELLO_BOARDS"
SYNC_TRELLO_LISTS = "SYNC_TRELLO_LISTS"
SYNC_TRELLO_LABELS = "SYNC_TRELLO_LABELS"

# WORKFLOW_STAGE_CHOICES
WF_UNDEFINED = "Undefined"
WF_OPEN = "Open"
WF_READY = "Ready"
WF_IN_PROGRESS = "In Progress"
WF_BLOCKED = "Blocked"
WF_CLOSED = "Closed"
WF_UNDEFINED_VALUE = 0
WF_OPEN_VALUE = 1
WF_READY_VALUE = 2
WF_IN_PROGRESS_VALUE = 3
WF_BLOCKED_VALUE = 4
WF_CLOSED_VALUE = 5
WORKFLOW_STAGE_CHOICES = [
    (WF_UNDEFINED_VALUE, WF_UNDEFINED),
    (WF_OPEN_VALUE, WF_OPEN),
    (WF_READY_VALUE, WF_READY),
    (WF_IN_PROGRESS_VALUE, WF_IN_PROGRESS),
    (WF_BLOCKED_VALUE, WF_BLOCKED),
    (WF_CLOSED_VALUE, WF_CLOSED)
]

DEFAULT_DUE_TIME = "18:29:59.000"
TRELLO_TIME_DELTA = timedelta(hours=5, minutes=30)

GREEN = "green"
YELLOW = "yellow"
OWNER_LABEL_NAME = "Owner"
COLLABORATOR_LABEL_NAME = "Collaborator"
OWNER_LABEL_COLOR = GREEN
COLLABORATOR_LABEL_COLOR = YELLOW

COLLABORATOR_CHECKLIST_NAME = "Collaborators"

# Checklist
CHECK_ITEM_INCOMPLETE = "incomplete"
CHECK_ITEM_COMPLETE = "complete"

# URLs
TRELLO_DOMAIN = "https://trello.com/"

