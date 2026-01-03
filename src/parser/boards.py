from aiohttp import ClientSession

class PdbBoardParser:
    def __init__(self, session: ClientSession):
        self._session = session

    async def posts_with_offset(
        self,
        topic_id: int,
        offset: int = 0,
        limit: int = 20,
        sort_type: str = 'new'
    ) -> dict:
        async with self._session.get(
            url='/api/v1/posts',
            params={
                'limit': limit,
                'topic_id': topic_id,
                'offset': offset,
                'sort_type': sort_type
            }
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def posts_with_cursor(
        self,
        topic_id: int,
        cursor: int = 0,
        limit: int = 20,
        sort_type: str = 'new'
    ) -> dict:
        async with self._session.get(
            url='/api/v1/postsWithCursor',
            params={
                'topic_id': topic_id,
                'cursor': cursor,
                'limit': limit,
                'sort_type': sort_type
            }
        ) as response:
            response.raise_for_status()
            return await response.json()
           
    async def post_comments(
        self,
        post_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> dict:
        async with self._session.get(
            url='/api/v1/post_comments',
            params={
                'post_id': post_id,
                'limit': limit,
                'offset': offset
            }
        ) as response:
            response.raise_for_status()
            return await response.json()