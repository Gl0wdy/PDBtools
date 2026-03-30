from aiohttp import ClientSession

class PdbProfileParser:
    def __init__(self, session: ClientSession):
        self._session = session

    async def pages_with_offset(
        self,
        property_id: int,
        offset: int = 0,
        limit: int = 100,
        sort: str = 'top'
    ) -> dict:
        async with self._session.get(
            url='api/v1/profiles',
            params={
                'limit': limit,
                'offset': offset,
                'property_id': property_id,
                'sort': sort
            }
        ) as response:
            response.raise_for_status()
            return await response.json(encoding='utf8')
        
    async def comments(
        self,
        profile_id: int,
        sort: str = "NEW",
        offset: int = 0,
        range: str = 'all',
        limit: int = 20
    ) -> dict:
        async with self._session.get(
            url=f'/api/v1/comments/{profile_id}',
            params={
                'sort': sort,
                'offset': offset,
                'range': range,
                'limit': limit
            }
        ) as response:
            response.raise_for_status()
            return await response.json(encoding='utf-8')