from .parent import TrelloParent


class TrelloListModule(TrelloParent):
    def get_cards_in_lists(self, list_ids):
        endpoint = "1/lists/{}/cards"
        return self.perform_trello_action(list_ids, endpoint)

    def update_list(self, list_id, **kwargs):
        endpoint = f"1/lists/{list_id}"
        payload_data = {}
        for key, value in kwargs.items():
            payload_data.update({key: value})
        return self.trello_api_response(endpoint, payload_data, request_type="PUT")

