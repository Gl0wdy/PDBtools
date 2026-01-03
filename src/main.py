from parser import PDBParser
from account import AccountManager

import asyncio
import time
import json


async def main():
    manager = AccountManager()
    manager.set_current_account(0)
    
    start = time.perf_counter()
    async with PDBParser(manager) as parser:
        tasks = (parser.board.posts_with_offset(327817, offset, 100) for offset in range(0, 1000, 100))
        res = await asyncio.gather(*tasks)
    all_posts = []
    for i in res:
        all_posts.extend(i['posts'])
    with open('res.json', 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=4)
    print(time.perf_counter() - start)

asyncio.run(main())