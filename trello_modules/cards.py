from .parent import TrelloParent


class TrelloCardModule(TrelloParent):
    def get_card(self, card_id):
        endpoint = f"/1/cards/{card_id}"
        return self.trello_api_response(endpoint)

    def create_card(self, **kwargs):
        # kwargs keys = name, pos, idList, idLabels:list, start, due, dueComplete
        endpoint = "1/cards"
        payload_data = {}
        for key, value in kwargs.items():
            payload_data.update({key: value})
        return self.trello_api_response(endpoint, payload_data, request_type="POST")

    def update_card(self, card_id, **kwargs):
        # https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-cards-id-put
        endpoint = f"1/cards/{card_id}"
        payload_data = {}
        for key, value in kwargs.items():
            payload_data.update({key: value})
        return self.trello_api_response(endpoint, payload_data, request_type="PUT")

    def create_attachment_on_card(self, card_id, **kwargs):
        # name, url, setCover:bool
        endpoint = f"1/cards/{card_id}/attachments"
        payload_data = {}
        for key, value in kwargs.items():
            payload_data.update({key: value})
        return self.trello_api_response(endpoint, payload_data, request_type="POST")

    def get_attachments_on_card(self, card_id):
        endpoint = f"1/cards/{card_id}/attachments"
        return self.trello_api_response(endpoint)

    def remove_label_from_card(self, card_id, label_id):
        endpoint = f"1/cards/{card_id}/idLabels/{label_id}"
        return self.trello_api_response(endpoint, request_type="POST")

    def checklists_on_card(self, card_id):
        endpoint = f"1/cards/{card_id}/checklists"
        return self.trello_api_response(endpoint)

    def update_checkitem_on_card(self, card_id, checkitem_id, **kwargs):
        endpoint = f"1/cards/{card_id}/checkItem/{checkitem_id}"
        payload_data = {}
        for key, value in kwargs.items():
            payload_data.update({key: value})
        return self.trello_api_response(endpoint, payload_data, request_type="PUT")

    def get_checklist_details(self, checklist_ids):
        endpoint = "1/checklists/{}"
        return self.perform_trello_action(checklist_ids, endpoint)
