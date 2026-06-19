import asyncio
from TechVJ.bot import StreamBot
from config import LOG_CHANNEL

async def main():
    await StreamBot.start()
    print("Bot started.")
    try:
        msg = await StreamBot.get_messages(LOG_CHANNEL, 94965)
        print("Message:", msg)
        if msg.empty:
            print("Message is empty!")
        else:
            print("Media:", msg.media)
    except Exception as e:
        print("Error fetching message:", e)
    await StreamBot.stop()

if __name__ == "__main__":
    asyncio.run(main())
