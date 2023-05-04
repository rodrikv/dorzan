import requests


class BotAdmins:
    def __init__(self, ids: list) -> None:
        self.ids = ids

    def add_admin(self, admin_id: int):
        self.admins.append(admin_id)


class TelegramBot:
    def __init__(self, token, admins: BotAdmins) -> None:
        self.token = token
        self.admins = admins
        self.parse_modes = ["markdown", "html"]

    def send_message(self, message, chat_id, parse_mode="markdown"):
        if parse_mode not in self.parse_modes:
            parse_mode = "markdown"

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode,
        }
        requests.post(url, data=data)

    def broadcast(self, message, chat_ids, parse_mode=None):
        for chat_id in chat_ids:
            self.send_message(message, chat_id, parse_mode)

    def broadcast_admins(self, message, parse_mode=None):
        for admin in self.admins:
            self.send_message(message, admin, parse_mode)