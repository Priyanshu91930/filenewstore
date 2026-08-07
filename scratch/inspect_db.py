import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Add workspace path to python search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import DB_URI

async def main():
    client = AsyncIOMotorClient(DB_URI)
    db = client["cloned_vjbotz"]
    print("Listing all razorpay_plans:")
    cursor = db.razorpay_plans.find({})
    async for doc in cursor:
        print(doc)
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
