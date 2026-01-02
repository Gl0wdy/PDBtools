from parser import PDBParser
from account import AccountManager

import asyncio

async def main():
    manager = AccountManager()
    await manager.load()
    print(manager.accounts)

asyncio.run(main())