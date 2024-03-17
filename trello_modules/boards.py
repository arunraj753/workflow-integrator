from .parent import TrelloParent


class TrelloBoardModule(TrelloParent):
    def get_user_boards(self):
        endpoint = "1/members/me/boards"
        payload_data = {"fields": "name"}
        return self.trello_api_response(endpoint, payload_data)

    def get_cards_on_board(self, board_id):
        endpoint = f"1/boards/{board_id}/cards"
        return self.trello_api_response(endpoint)

    def get_lists_on_boards(self, board_ids):
        endpoint = "1/boards/{}/lists"
        return self.perform_trello_action(board_ids, endpoint)

    def get_labels_on_boards(self, board_ids):
        endpoint = "1/boards/{}/labels"
        return self.perform_trello_action(board_ids, endpoint)

    def create_labels_on_board(self, **kwargs):
        # kwargs --> 'name': '{name}', 'color': '{color}', 'idBoard': '{idBoard}',
        endpoint = "1/labels"
        payload_data = {}
        for key, value in kwargs.items():
            payload_data.update({key: value})
        return self.trello_api_response(endpoint, payload_data, request_type="POST")

    def create_list_on_board(self, **kwargs):
        # kwargs --> 'name': '{name}', 'idBoard': '{idBoard}', 'pos': 'bottom'
        endpoint = "1/lists"
        payload_data = {}
        for key, value in kwargs.items():
            payload_data.update({key: value})
        # response
        # dict_keys(['id', 'name', 'closed', 'idBoard', 'pos', 'subscribed', 'softLimit', 'status'])
        return self.trello_api_response(endpoint, payload_data, request_type="POST")
