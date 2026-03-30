from parser import PDBParser
from account import AccountManager

import asyncio
import time
import json
from datetime import datetime as dt
import pandas as pd


async def main():
    pd.set_option('display.max_rows', None)
    manager = AccountManager()
    manager.set_current_account(0)
    
    start = time.perf_counter()

    async with PDBParser(manager) as parser:
        res = await parser.board_posts(327817, dt(2025, 1, 1).date())
        print(len(res))

    df = pd.read_json('result.json')
    df['username'] = df['username'].apply(lambda u: f"@[{u}]")
    likes_by_user = df.groupby('username')['vote_count'].sum()

    # Сортируем по количеству лайков (по убыванию)
    likes_by_user = likes_by_user.sort_values(ascending=False)

    # Выводим результат
    print(likes_by_user)

asyncio.run(main())