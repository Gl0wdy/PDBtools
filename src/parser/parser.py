import aiohttp
from datetime import date, datetime as dt
from typing import Literal
import asyncio

from account import AccountManager
from .boards import PdbBoardParser
from .profiles import PdbProfileParser


class PDBParser:
    def __init__(self, account_manager: AccountManager):
        self.manager = account_manager
        self.board = None
        self.profile = None
        self._session = None

    async def board_posts(
        self,
        topic_id: int,
        until_date: date | None = None,
        until_count: int | None = None,
        parse_by: Literal['offset', 'cursor'] = 'cursor'
    ):
        if not until_date and not until_count:
            raise ValueError('One of until_date|until_count must be provided')

        match parse_by:
            case 'cursor':
                cursor = 0
                total_posts = []
                while True:
                    response = await self.board.posts_with_cursor(
                        topic_id, cursor, limit=100
                    )
                    if until_date is not None:
                        for post in response['posts']:
                            create_date = dt.fromtimestamp(post['create_date'] // 1000).date()
                            if create_date < until_date:
                                return total_posts
                            total_posts.append(post)
                    else: 
                        if len(total_posts) >= until_count:
                            return total_posts
                        total_posts.extend(response['posts'])
                    cursor = response['cursor']

    async def get_profiles(
        self,
        property_id: int,
        sort: str = 'top',
        add_comments: bool = False,
        amount: int = 100
    ) -> list:
        total_profiles = []
    
        batches = []
        remaining = amount
        offset = 0
        while remaining > 0:
            limit = min(100, remaining)
            batches.append((offset, limit))
            offset += limit
            remaining -= limit
        
        tasks = (
            self.profile.pages_with_offset(property_id, offset, limit, sort)
            for offset, limit in batches
        )
        result = await asyncio.gather(*tasks)
        for r in result:
            total_profiles.extend(r['profiles'])

        if add_comments:
            profiles_by_id = {i['id']: i for i in total_profiles}
            tasks = (
                self.profile.comments(i, sort, 0, 'all', 20)
                for i in profiles_by_id 
            )
            result = await asyncio.gather(*tasks)
            for raw_resp in result:
                comments = raw_resp['comments']
                target_profile = profiles_by_id[comments[0]['profile_id']]
                target_profile['comments'] = comments
            total_profiles = list(profiles_by_id.values())

        return total_profiles
        
            
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
        self.profile = PdbProfileParser(self._session)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.close()