import aiohttp

class PDBParser:
    def __init__(self):
        self._session = None
        self._boards_parser = None
        self._pages_parser = None

    async def posts_with_cursor(
        self,
        topic_id: int,
        cursor: int,
        limit: int = 20
    ) -> dict:
        async with self._session.get(
            url='/postsWithCursor',
            params={
                'topic_id': topic_id,
                'cursor': cursor,
                'limit': limit
            }
        ) as response:
            if response.ok:
                return await response.json()
            response.raise_for_status()
            
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            base_url='https://api.personality-database.com/api/v1/'
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.close()