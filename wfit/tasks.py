from datetime import date, datetime

from helpers.trello_helper import TrelloHelper
from server.settings import logger
from trello_modules.boards import TrelloBoardModule
from trello_modules.cards import TrelloCardModule
from trello_modules.labels import TrelloLabelModule
from trello_modules.lists import TrelloListModule
from utils.constants import SYNC_TRELLO_BOARDS, SYNC_TRELLO_LISTS, SYNC_TRELLO_LABELS, WF_UNDEFINED, TRELLO_TIME_DELTA, \
    WF_CLOSED_VALUE, WF_IN_PROGRESS_VALUE, DEFAULT_DUE_TIME, COLLABORATOR_LABEL_NAME, OWNER_LABEL_NAME, \
    COLLABORATOR_CHECKLIST_NAME, TRELLO_DOMAIN, CHECK_ITEM_COMPLETE
from utils.utils import string_to_bool, get_required_batches, trello_date_to_python_date
from wfit.models import TrelloBoard, GlobalConfig, TrelloList, TrelloLabel, JobCard, JobTracker, Project, Release

TRELLO_API_BATCH_SIZE = 10


class TrelloModule(TrelloBoardModule, TrelloCardModule, TrelloLabelModule, TrelloListModule):
    pass


trello = TrelloModule()


class WorkFlowIntegrator:
    def __init__(self):
        self.all_tracked_trello_cards = []
        self.helper = TrelloHelper()
        self.current_board = None

    def logger(self, message, log_level="info"):
        final_message = ""
        if self.current_board:
            final_message += f"{self.current_board}|"
        final_message += message
        print(final_message)
        logger.info(final_message)

    def sync_trello_boards(self):
        trello_board_sync = True
        config_obj = GlobalConfig.objects.filter(name=SYNC_TRELLO_BOARDS).first()
        if config_obj:
            if not string_to_bool(config_obj.value):
                trello_board_sync = False

        if not trello_board_sync:
            self.logger("trello_board_sync is False")
            return
        self.logger("Starting sync_trello_boards")
        trello_boards_fetched = trello.get_user_boards()
        self.logger(f"Trello Boards Fetched : {trello_boards_fetched}")
        trello_board_pk_list = []
        trello_board_id_list = TrelloBoard.objects.values_list('trello_board_id', flat=True)
        for trello_board_details in trello_boards_fetched:
            board_name = trello_board_details["name"]
            board_id = trello_board_details["id"]
            if board_id in trello_board_id_list:
                continue
            obj, created = TrelloBoard.objects.update_or_create(
                trello_board_id=board_id, trello_board_name=board_name, is_active=True)
            trello_board_pk_list.append(obj.id)
        TrelloBoard.objects.exclude(id__in=trello_board_pk_list).update(is_active=False)

        if config_obj:
            config_obj.value = False
            config_obj.save()
        else:
            GlobalConfig.objects.create(name=SYNC_TRELLO_BOARDS, value="False")
        # web_trello_board_dict = convert_records_to_dict(web_trello_boards, "name", "id")

    def sync_trello_lists(self):
        self.logger("Starting sync_trello_lists()")
        trello_list_sync = True
        config_obj = GlobalConfig.objects.filter(name=SYNC_TRELLO_LISTS).first()
        if config_obj:
            if not string_to_bool(config_obj.value):
                trello_list_sync = False

        if not trello_list_sync:
            self.logger("trello_list_sync is False")
            return

        self.logger("Starting sync_trello_lists")
        working_board_ids = TrelloBoard.objects.filter(
            is_working_board=True, is_active=True).values_list('trello_board_id', flat=True)

        trello_board_id_list = []
        for trello_board_id in working_board_ids:
            trello_board_id_list.append(trello_board_id)

        if not trello_board_id_list:
            self.logger("trello_board_id_list is empty")
            raise Exception(
                "Please make sure there is at least one TrelloBoard with is_working_board=True and is_active=True")
        self.logger("Fetching lists_on_board.")
        response_json = trello.get_lists_on_boards(trello_board_id_list)
        self.logger("Fetched lists_on_board.")
        for list_details in response_json:
            list_id = list_details["id"]
            list_name = list_details["name"]
            list_board_id = list_details["idBoard"]
            board_instance = self.helper.get_trello_board_instance(list_board_id)
            obj, created = TrelloList.objects.update_or_create(
                trello_list_id=list_id, trello_list_name=list_name,
                board=board_instance)
        self.logger("TrelloList model update_or_create completed")
        if config_obj:
            config_obj.value = False
            config_obj.save()
        else:
            GlobalConfig.objects.create(name=SYNC_TRELLO_LISTS, value="False")

        self.logger("Completed sync_trello_lists()")

    def sync_trello_labels(self):
        self.logger("Starting sync_trello_labels()")
        trello_label_sync = True
        config_obj = GlobalConfig.objects.filter(name=SYNC_TRELLO_LABELS).first()
        if config_obj:
            if not string_to_bool(config_obj.value):
                trello_label_sync = False

        if not trello_label_sync:
            self.logger("trello_label_sync is False")
            return

        self.logger("Starting sync_trello_labels")
        working_board_ids = TrelloBoard.objects.filter(
            is_working_board=True, is_active=True).values_list('trello_board_id', flat=True)
        # TrelloList.objects.all()
        trello_board_id_list = []
        for trello_board_id in working_board_ids:
            trello_board_id_list.append(trello_board_id)

        self.logger("Fetching labels_on_board.")
        labels_on_boards = trello.get_labels_on_boards(trello_board_id_list)
        self.logger("Fetched labels_on_board.")
        for label_details in labels_on_boards:
            label_id = label_details["id"]
            label_name = label_details["name"]
            label_board_id = label_details["idBoard"]
            label_color = label_details["color"]
            board_instance = self.helper.get_trello_board_instance(label_board_id)
            if label_name:
                obj, created = TrelloLabel.objects.update_or_create(
                    trello_label_id=label_id, trello_label_name=label_name,
                    trello_label_color=label_color, board=board_instance)
        self.logger("TrelloLabel model update_or_create completed")
        if config_obj:
            config_obj.value = False
            config_obj.save()
        else:
            GlobalConfig.objects.create(name=SYNC_TRELLO_LABELS, value="False")

        self.logger("Completed sync_trello_labels()")

    def get_tracked_trello_cards(self):
        self.logger("Starting get_tracked_trello_cards()")
        all_tracked_trello_cards = []
        trello_list_ids = []
        trello_list_id_queryset = TrelloList.objects.exclude(
            workflow_stage=0).values_list('trello_list_id', flat=True)

        if not trello_list_id_queryset:
            raise Exception("Please make sure there is at least one list with workflow_stage_value greater than 0")
        for trello_list_id in trello_list_id_queryset:
            trello_list_ids.append(trello_list_id)
        required_batches = get_required_batches(trello_list_ids, TRELLO_API_BATCH_SIZE)
        self.logger(f"Required batches to pull trello cards from all boards: {required_batches}")

        for i in range(0, required_batches):
            self.logger(f"Starting Batch: {i}")
            start_index = i * TRELLO_API_BATCH_SIZE
            end_index = start_index + TRELLO_API_BATCH_SIZE
            trello_list_ids_in_batch = trello_list_ids[start_index:end_index]
            tracked_cards = trello.get_cards_in_lists(list_ids=trello_list_ids_in_batch)
            all_tracked_trello_cards.extend(tracked_cards)
            self.logger(f"Pulled trello cards from batch:{i}")

        self.logger(f"Tracked trello cards count: {len(all_tracked_trello_cards)}")
        self.logger("Completed get_tracked_trello_cards()")
        return all_tracked_trello_cards

    def update_start_and_due(self, trello_card):
        update_dict = {}
        card_is_done = trello_card["dueComplete"]
        card_due_date = trello_card['due']
        card_start_date = trello_card['start']
        start_date = None
        due_date = None
        due_complete = None
        trello_list_obj = self.helper.get_trello_list_instance(trello_list_id=trello_card["idList"])

        # if trello_list_obj.workflow_stage is less than 'In Progress', no need to update any dates
        if trello_list_obj.workflow_stage < WF_IN_PROGRESS_VALUE:
            return update_dict

        if not card_start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
            if card_due_date:
                date_string = card_due_date.split("T")[0]
                time_string = card_due_date.split("T")[1].split(".000Z")[0]
                card_due_date_ist = datetime.strptime(
                    f"{date_string} {time_string}",
                    '%Y-%m-%d %H:%M:%S') + TRELLO_TIME_DELTA
                if datetime.combine(date.today(), datetime.min.time()) > card_due_date_ist:
                    start_date = None

        if trello_list_obj.workflow_stage == WF_CLOSED_VALUE:
            if not card_due_date:
                due_date = datetime.now().strftime(f"%Y-%m-%dT{DEFAULT_DUE_TIME}Z")
            if not card_is_done:
                due_complete = "true"

        if start_date:
            update_dict.update({"start": start_date})
        if due_date:
            update_dict.update({"due": due_date})
        if due_complete:
            update_dict.update({"dueComplete": due_complete})

        return update_dict

    def update_checklist_of_card(self, trello_card):
        checklist_ids = trello_card["idChecklists"]

        if not checklist_ids:
            return

        card_list_id = trello_card["idList"]
        board_id = trello_card["idBoard"]
        collaborator_trello_list_id = self.helper.get_collaborator_list_id(board_id, card_list_id)
        if not collaborator_trello_list_id:
            collaborator_trello_list_id = card_list_id
        card_id = trello_card["id"]
        checklists_data = trello.get_checklist_details(checklist_ids)
        if not isinstance(checklists_data, list):
            checklists_data = [checklists_data]

        owner_label_id = self.helper.get_label_ids(board_id=board_id, label_names_list=[OWNER_LABEL_NAME])[0]
        collaborator_label_id = self.helper.get_label_ids(
            board_id=board_id, label_names_list=[COLLABORATOR_LABEL_NAME])[0]

        trello_card_label_ids = [label_data["id"] for label_data in trello_card["labels"]]
        add_owner_label = False if owner_label_id in trello_card_label_ids else True
        collaborator_card_label_ids = [label_id for label_id in trello_card_label_ids if label_id != owner_label_id]
        collaborator_card_label_ids.append(collaborator_label_id)
        collaborator_card_label_ids = list(set(collaborator_card_label_ids))

        has_collaborator_cards = False
        for checklist_data in checklists_data:
            if not checklist_data["name"] == COLLABORATOR_CHECKLIST_NAME:
                continue
            has_collaborator_cards = True
            check_items_list = checklist_data["checkItems"]
            for check_item in check_items_list:
                check_item_id = check_item["id"]
                check_item_name = check_item["name"]
                check_item_state = check_item["state"]
                if check_item_state == CHECK_ITEM_COMPLETE:
                    continue
                if check_item_name.startswith(TRELLO_DOMAIN):
                    continue
                self.logger(f"Creating a new card from checklist. Card name:{check_item_name}")
                response_json = trello.create_card(
                    name=check_item_name, idList=collaborator_trello_list_id, idLabels=collaborator_card_label_ids)
                trello.create_attachment_on_card(card_id=response_json["id"], name="Owner", url=trello_card["url"])
                check_item_updated_name = response_json["url"]
                self.logger(f"Created a new card. Card name:{check_item_name}")
                self.logger(f"Updating check item on checklist with url:{check_item_updated_name}")
                trello.update_checkitem_on_card(card_id=card_id, checkitem_id=check_item_id,
                                                name=check_item_updated_name)
                self.logger(f"Created new card from checklist. Card name:{check_item_name}")

        if has_collaborator_cards:
            if add_owner_label:
                self.logger(f"Adding Owner Label. Card Name : {trello_card['name']}")
                owner_label_ids = trello_card_label_ids + [owner_label_id]
                trello.update_card(card_id, idLabels=owner_label_ids)
                self.logger(f"Added Owner Label. Card Name : {trello_card['name']}")
        else:
            self.logger(f"Collaborator cards not found. Card Name : {trello_card['name']}")

    def update_trello_card(self, trello_card):
        trello_card_updated = trello_card
        card_update_args = self.update_start_and_due(trello_card)
        if card_update_args:
            self.logger(f"Updating start_and_due.Card name: {trello_card['name']}")
            self.logger(f"Update Args : {card_update_args}")
            trello_card_updated = trello.update_card(card_id=trello_card["id"], **card_update_args)
            self.logger(f"Updated start_and_due.Card name: {trello_card['name']}")
        else:
            self.logger(f"start_and_due update not required.Card Name: {trello_card['name']}")
        self.update_checklist_of_card(trello_card=trello_card_updated)
        return trello_card_updated

    def create_job_card(self, trello_card):
        trello_board_obj = self.helper.get_trello_board_instance(trello_board_id=trello_card["idBoard"])
        trello_list_obj = self.helper.get_trello_list_instance(trello_list_id=trello_card["idList"])
        self.logger(f"Creating JobCard. Card name: {trello_card['name']}")
        job_card_created_obj = JobCard.objects.create(
            trello_card_id=trello_card["id"], name=trello_card["name"],
            trello_board=trello_board_obj, trello_list=trello_list_obj,
            short_url=trello_card["shortUrl"], id_short=trello_card["idShort"]
        )
        self.logger(f"Created JobCard. Card name: {trello_card['name']}")
        return job_card_created_obj

    # def get_or_create_release(self, trello_card):
    #     release_name = trello_card["name"]
    #     self.logger(f"get_or_create. Release name : {release_name}")
    #     release_obj, created = Release.objects.get_or_create(name=release_name)
    #     return release_obj

    def get_or_create_project(self, project_name):
        self.logger(f"get_or_create. Project name : {project_name}")
        project_obj, created = Project.objects.get_or_create(name=project_name, label_name=project_name)
        return project_obj

    def update_job_card(self, trello_card, job_card_obj):
        update = False
        trello_card_name = trello_card["name"]
        if trello_card_name != job_card_obj.name:
            job_card_obj.name = trello_card_name
            update = True
        project_obj, project_name = self.helper.get_project(trello_card)
        if project_obj:
            if job_card_obj.project != project_obj:
                job_card_obj.project = project_obj
                update = True

        if not project_obj and project_name:
            project_obj = self.get_or_create_project(project_name)
            job_card_obj.project = project_obj
            update = True

        if update:
            self.logger(f"Updating JobCard. Card name: {trello_card_name}")
            job_card_obj.save()

    def create_job_tracker(self, trello_card, job_card_obj):
        self.logger(f"Creating job_tracker for {trello_card['name']}")
        trello_start_date = trello_date_to_python_date(trello_card["start"])
        trello_due_date = trello_date_to_python_date(trello_card["due"])
        is_completed = trello_card["dueComplete"]
        actual_finish = None
        if is_completed:
            actual_finish = trello_due_date

        job_tracker_new_obj = JobTracker.objects.create(
            job_card=job_card_obj, planned_start=trello_start_date, planned_finish=trello_due_date,
            actual_start=trello_start_date, actual_finish=actual_finish, current_due=trello_due_date,
            is_completed=is_completed)
        self.logger(f"Created job_tracker for {trello_card['name']}")
        return job_tracker_new_obj

    def update_job_tracker(self, trello_card, job_tracker_obj):
        self.logger(f"Updating job_tracker for the card: {trello_card['name']}")
        trello_start_date = trello_date_to_python_date(trello_card["start"])
        trello_due_date = trello_date_to_python_date(trello_card["due"])
        trello_is_completed = trello_card["dueComplete"]
        save_obj = False

        if not job_tracker_obj.planned_start and trello_start_date:
            self.logger("Adding planned_start")
            job_tracker_obj.planned_start = trello_start_date
            save_obj = True
        if not job_tracker_obj.planned_finish and trello_due_date:
            self.logger("Adding planned_finish")
            job_tracker_obj.planned_finish = trello_due_date
            save_obj = True
        if not job_tracker_obj.actual_start and trello_start_date:
            self.logger("Adding actual_start")
            job_tracker_obj.actual_start = trello_start_date
            save_obj = True

        if trello_is_completed:
            if job_tracker_obj.actual_finish != trello_due_date:
                self.logger("Updating actual_finish")
                job_tracker_obj.actual_finish = trello_due_date
                save_obj = True
            if job_tracker_obj.current_due:
                if job_tracker_obj.current_due < trello_due_date:
                    self.logger("Updating current_due after comparison")
                    job_tracker_obj.current_due = trello_due_date
                    save_obj = True
            else:
                self.logger("Adding current_due")
                job_tracker_obj.current_due = trello_due_date
                save_obj = True

            if not job_tracker_obj.is_completed:
                self.logger("Updating is_completed")
                job_tracker_obj.is_completed = True
                save_obj = True
        else:
            if job_tracker_obj.current_due != trello_due_date:
                self.logger("Updating current_due")
                job_tracker_obj.current_due = trello_due_date
                save_obj = True

        if save_obj:
            job_tracker_obj.save()
            self.logger(f"Updated job_tracker for the card: {trello_card['name']}")
        else:
            self.logger(f"Up-to-date job_tracker for the card: {trello_card['name']}")

    def sync_job_card(self, trello_card):
        self.logger("Starting sync_job_card")
        self.current_board = self.helper.get_trello_board_name(trello_card["idBoard"])
        job_card_obj = JobCard.objects.filter(trello_card_id=trello_card["id"]).first()

        if job_card_obj:
            self.update_job_card(trello_card, job_card_obj)
        else:
            job_card_obj = self.create_job_card(trello_card)

        job_tracker_obj = JobTracker.objects.filter(job_card=job_card_obj).first()

        if job_tracker_obj:
            self.update_job_tracker(trello_card=trello_card, job_tracker_obj=job_tracker_obj)
        else:
            self.create_job_tracker(trello_card=trello_card, job_card_obj=job_card_obj)

    def perform_card_integration(self):
        self.logger("Starting update_trello_cards()")
        self.all_tracked_trello_cards = self.get_tracked_trello_cards()
        for trello_card in self.all_tracked_trello_cards:
            trello_card_updated = self.update_trello_card(trello_card)
            self.sync_job_card(trello_card_updated)

    def run(self):
        logger.info("run")
        self.sync_trello_boards()
        self.helper.setup()
        self.sync_trello_lists()
        self.sync_trello_labels()
        self.helper.initialize()
        self.perform_card_integration()
        return True


def run_workflow_integrator():
    workflow = WorkFlowIntegrator()
    return workflow.run()
