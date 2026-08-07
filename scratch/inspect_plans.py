import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import DB_URI

async def main():
    client = AsyncIOMotorClient(DB_URI)
    db = client["cloned_vjbotz"]
    print("Listing plans_config:")
    cursor = db.plans_config.find({})
    async for doc in cursor:
        out = repr(doc).encode('ascii', 'backslashreplace').decode('ascii')
        print(out)
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
