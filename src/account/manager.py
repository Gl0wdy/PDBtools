from .account import Account

from slugify import slugify
from config import BASE_DIR
import json
import os


class AccountManager:
    ACCOUNTS_FOLDER = BASE_DIR / 'data/accounts/'
    current_account = None

    def __init__(self, path: str = ""):
        self.accounts: list[Account] = []
        for file in self.ACCOUNTS_FOLDER.iterdir():
            if file.is_file():
                self._load_account(file)

        if path:
            self._path = BASE_DIR / path
        else:
            self._path = self.ACCOUNTS_FOLDER

    def add_account(self, user_data: dict, cookies: dict):
        cookies = {i['name']: i['value'] for i in cookies}
        user_data.update({'cookies': cookies})
        account = Account.from_dict(user_data)
        self.current_account = account
        self.accounts.append(account)

        with open(self._path / f'{slugify(account.name)}.json', 'w', encoding='utf-8') as file:
            json.dump(user_data, file, ensure_ascii=False, indent=4)

    def delete_account(self, index: int):
        account = self.accounts[index]
        os.remove(self.ACCOUNTS_FOLDER / f'{account.name}.json')

    def set_current_account(self, index: int):
        self.current_account = self.accounts[index]
        
    def _load_account(self, file):
        try:
            with file.open('r', encoding='utf-8') as f:
                text = f.read()
                data = json.loads(text)
                self.accounts.append(Account.from_dict(data))
        except:
            raise RuntimeError(f"Something went wrong during {file} processing.")