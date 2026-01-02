from pathlib import Path
from config import BASE_DIR
import json

import asyncio
import aiofiles



class AccountManager:
    ACCOUNTS_FOLDER = BASE_DIR / 'data/accounts/'

    def __init__(self):
        self.accounts = []

    async def load(self):
        tasks = [self._load_account(file) for file in self.ACCOUNTS_FOLDER.iterdir() if file.is_file()]
        await asyncio.gather(*tasks)
        return self
    
    async def add_account(self, account_data: dict, cookies: dict):

    async def _load_account(self, file):
        async with aiofiles.open(file, 'r', encoding='utf-8') as f:
            text = await f.read()
            data = json.loads(text)
            self.accounts.append(data)