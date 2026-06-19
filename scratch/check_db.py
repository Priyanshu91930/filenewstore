import asyncio
import motor.motor_asyncio
from config import DB_URI

async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
    db = client["cloned_vjbotz"]
    
    print("Searching clone_files for ID starting with 35a2bc...")
    async for doc in db.clone_files.find({"_id": {"$regex": "^35a2bc"}}):
        print(doc)
        
    print("\nSearching bots collection...")
    async for bot in db.bots.find():
        print(f"Bot: {bot.get('username')}, ID: {bot.get('bot_id')}")

if __name__ == "__main__":
    asyncio.run(main())
