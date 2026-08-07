import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from clone_plugins.commands import create_razorpay_subscription

async def main():
    # Test ₹199 monthly subscription
    print("Testing create_razorpay_subscription for ₹199 Monthly:")
    res = await create_razorpay_subscription(
        amount_inr=199,
        plan_duration="1 Month",
        user_id=8494193109,
        bot_id=12345,
        bot_username="test_bot"
    )
    print(f"Result: {res}")

if __name__ == "__main__":
    asyncio.run(main())
