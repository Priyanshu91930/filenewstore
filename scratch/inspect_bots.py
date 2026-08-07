import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import DB_URI

async def main():
    client = AsyncIOMotorClient(DB_URI)
    db = client["cloned_vjbotz"]
    print("Checking bots collection for razorpay:")
    cursor = db.bots.find({})
    async for doc in cursor:
        out = {k: v for k, v in doc.items() if "razorpay" in k.lower()}
        if out:
            print(f"Bot Username: {doc.get('username')} | Custom Razorpay fields: {out}")
        else:
            print(f"Bot Username: {doc.get('username')} | No custom razorpay fields.")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
