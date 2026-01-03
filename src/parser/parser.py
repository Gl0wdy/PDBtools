import aiohttp

from account import AccountManager
from .boards import PdbBoardParser


class PDBParser:
    def __init__(self, account_manager: AccountManager):
        self.manager = account_manager
        self._session = None
        self.board = None
        self.page = None
            
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            base_url='https://api.personality-database.com/',
            cookies=self.manager.current_account.cookies,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.personality-database.com/",
                "Origin": "https://www.personality-database.com",
            }
        )
        self.board = PdbBoardParser(self._session)
        self.page = ...
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.close()