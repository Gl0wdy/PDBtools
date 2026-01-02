class Account:
    def __init__(self, json_data: dict):
        self.name = json_data['name']
        self.id = json_data['id']
        self.cookies = json_data['cookies']