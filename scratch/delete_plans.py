import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import DB_URI

async def main():
    client = AsyncIOMotorClient(DB_URI)
    db = client["cloned_vjbotz"]
    print("Deleting all cached plans from razorpay_plans collection...")
    res = await db.razorpay_plans.delete_many({})
    print(f"Deleted {res.deleted_count} plans.")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
