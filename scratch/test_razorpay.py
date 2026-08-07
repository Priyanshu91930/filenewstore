import asyncio
import aiohttp
import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

async def main():
    auth = aiohttp.BasicAuth(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
    
    # Generate a random amount to ensure we create a new plan
    amount_inr = random.randint(200, 1000)
    print(f"Creating a new plan for amount: {amount_inr} INR")
    
    plan_payload = {
        "period": "monthly",
        "interval": 1,
        "item": {
            "name": f"Test Plan {amount_inr}",
            "amount": amount_inr * 100,
            "currency": "INR",
            "description": "Test subscription plan"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        # 1. Create plan
        async with session.post("https://api.razorpay.com/v1/plans", json=plan_payload, auth=auth) as resp:
            print(f"Plan Creation Status: {resp.status}")
            plan_res = await resp.json()
            print(f"Plan Response: {plan_res}")
            plan_id = plan_res.get("id")
            
        if not plan_id:
            print("Plan creation failed!")
            return
            
        # 2. Create subscription
        sub_payload = {
            "plan_id": plan_id,
            "total_count": 12,
            "quantity": 1,
            "customer_notify": 1,
            "notes": {
                "user_id": "8494193109",
                "bot_id": "12345",
                "bot_username": "test_bot"
            }
        }
        async with session.post("https://api.razorpay.com/v1/subscriptions", json=sub_payload, auth=auth) as resp:
            print(f"Subscription Creation Status: {resp.status}")
            print(f"Subscription Response: {await resp.text()}")

if __name__ == "__main__":
    asyncio.run(main())
