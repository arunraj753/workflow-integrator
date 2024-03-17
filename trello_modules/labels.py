from .parent import TrelloParent


class TrelloLabelModule(TrelloParent):
    pass


    # def create_label_on_board(self, name, color, idBoard):
    #     # query = {
    #     #     'name': '{name}',
    #     #     'color': '{color}',
    #     #     'idBoard': '{idBoard}',
    #     # }
    #     endpoint = f"1/labels"
    #     payload_data = {}
    #     for key, value in kwargs.items():
    #         payload_data.update({key: value})
    #     return self.trello_api_response(endpoint, payload_data, request_type="POST")
