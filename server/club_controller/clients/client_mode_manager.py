from club_controller.clients.client_mode import ClientModeId

"""
ClientModeManager central point which keeps the current mode for the clients
"""
class ClientModeManager:
    mode = ClientModeId.AUDIO

    def __init__(self, client_handler):
        self.client_handler = client_handler

    def change_mode(self, new_mode: ClientModeId):
        self.mode = ClientModeId
