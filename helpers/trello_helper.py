from server.settings import logger
from utils.constants import WF_READY_VALUE, BLUE_DARK
from wfit.models import TrelloBoard, TrelloList, TrelloLabel, Project, Release


class TrelloHelper:

    def __init__(self):

        self.global_dict = {}
        self.board_id_db_board_id = {}
        self.board_id_board_instance = {}
        self.board_id_board_name = {}
        self.list_id_list_instance = {}
        self.board_id_ready_list_id = {}
        self.label_id_name_dict = {}
        self.label_name_id_dict = {}
        self.project_name_id_dict = {}

    def logger(self, message, log_level="info"):
        logger.info(message)
        print(message)

    def setup(self):
        self.logger("Setting up Trello Helper")
        trello_board_queryset = TrelloBoard.objects.all()
        for queryset in trello_board_queryset:
            self.board_id_db_board_id.update({queryset.trello_board_id: queryset.id})
            self.board_id_board_instance.update({queryset.trello_board_id: queryset})
            self.board_id_board_name.update({queryset.trello_board_id: queryset.trello_board_name})
        self.logger("Completed helper setup()")

    def initialize(self):
        self.logger("Initializing Trello Helper")

        trello_list_queryset = TrelloList.objects.all()
        for trello_list_obj in trello_list_queryset:
            self.list_id_list_instance.update({trello_list_obj.trello_list_id: trello_list_obj})
            trello_board_id = trello_list_obj.board.trello_board_id
            if trello_list_obj.workflow_stage == WF_READY_VALUE:
                trello_list_id = trello_list_obj.trello_list_id
                self.board_id_ready_list_id.update({trello_board_id: trello_list_id})

        trello_label_queryset = TrelloLabel.objects.all()
        for trello_label_obj in trello_label_queryset:
            trello_board_id = trello_label_obj.board.trello_board_id
            trello_label_id = trello_label_obj.trello_label_id
            trello_label_name = trello_label_obj.trello_label_name
            self.label_id_name_dict.update({trello_label_id: trello_label_name})
            board_label_name_id_dict = self.label_name_id_dict.get(trello_board_id)
            if board_label_name_id_dict:
                board_label_name_id_dict.update({trello_label_name: trello_label_id})
            else:
                self.label_name_id_dict.update({trello_board_id: {trello_label_name: trello_label_id}})

        project_queryset = Project.objects.all()
        for project_obj in project_queryset:
            self.project_name_id_dict.update({project_obj.name: project_obj})

        release_queryset = Release.objects.all()
        for release_obj in release_queryset:
            self.project_name_id_dict.update({release_obj.name: release_obj})

    def get_trello_board_instance(self, trello_board_id):
        return self.board_id_board_instance[trello_board_id]

    def get_trello_list_instance(self, trello_list_id):
        return self.list_id_list_instance[trello_list_id]

    def get_trello_board_name(self, trello_board_id):
        return self.board_id_board_name[trello_board_id]

    def get_collaborator_list_id(self, board_id, card_list_id):
        source_list_workflow_value = self.get_trello_list_instance(card_list_id).workflow_stage
        ready_list_id = self.board_id_ready_list_id.get(board_id, None)
        if not ready_list_id:
            return card_list_id
        ready_list_workflow_value = self.get_trello_list_instance(ready_list_id).workflow_stage
        if source_list_workflow_value < ready_list_workflow_value:
            return card_list_id
        return ready_list_id

    def get_label_ids(self, board_id, label_names_list=None):
        self.logger("Inside get_label_ids()")
        label_ids = []
        board_label_name_id_dict = self.label_name_id_dict.get(board_id)
        for label_name, label_id in board_label_name_id_dict.items():
            if label_name in label_names_list:
                label_ids.append(label_id)
        return label_ids

    def get_project(self, trello_card):
        project_labels = []
        project_obj = None
        project_label_name = None
        for label_details in trello_card["labels"]:
            if label_details["color"] == BLUE_DARK:
                project_labels.append(label_details["name"])
        if len(project_labels) > 1:
            raise Exception(f"Multiple projects are associated with the card: {trello_card['name']}")
        if project_labels:
            project_label_name = project_labels[0]
            project_obj = self.project_name_id_dict.get(project_label_name, None)
        return project_obj, project_label_name
