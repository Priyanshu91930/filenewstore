import time
import logging
from plugins.clone import async_mongo_db as db

logger = logging.getLogger(__name__)

# Collection names:
# 1. referral_campaigns: Config per bot_id
# 2. referral_participants: Users who joined the campaign to get their links
# 3. referrals: Mapping of referred users to their referrers
# 4. referral_clicks: Unique file opens tracking

async def get_campaign(bot_id):
    """Retrieve campaign configuration for a bot."""
    try:
        return await db.referral_campaigns.find_one({"bot_id": int(bot_id)})
    except Exception as e:
        logger.error(f"Error getting campaign configuration: {e}")
        return None

async def set_campaign(bot_id, enabled=None, duration=None, channel=None):
    """Update campaign configuration."""
    try:
        update_fields = {}
        if enabled is not None:
            update_fields["enabled"] = bool(enabled)
            if enabled:
                update_fields["started_at"] = time.time()
        if duration is not None:
            update_fields["duration_days"] = int(duration)
        if channel is not None:
            update_fields["channel"] = channel

        await db.referral_campaigns.update_one(
            {"bot_id": int(bot_id)},
            {"$set": update_fields},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error setting campaign configuration: {e}")
        return False

async def is_campaign_active(bot_id):
    """Check if the campaign is active and not expired."""
    camp = await get_campaign(bot_id)
    if not camp or not camp.get("enabled"):
        return False
    
    started_at = camp.get("started_at", 0)
    duration_days = camp.get("duration_days", 7)
    if started_at > 0:
        elapsed = time.time() - started_at
        if elapsed > (duration_days * 86400):
            # Expired - disable it automatically
            await db.referral_campaigns.update_one({"bot_id": int(bot_id)}, {"$set": {"enabled": False}})
            return False
    return True

async def add_participant(bot_id, user_id):
    """Join the referral campaign."""
    try:
        await db.referral_participants.update_one(
            {"bot_id": int(bot_id), "user_id": int(user_id)},
            {"$set": {"joined_at": time.time()}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error adding participant: {e}")
        return False

async def is_participant(bot_id, user_id):
    """Check if a user has joined the referral campaign."""
    try:
        res = await db.referral_participants.find_one({"bot_id": int(bot_id), "user_id": int(user_id)})
        return res is not None
    except Exception as e:
        logger.error(f"Error checking participant: {e}")
        return False

async def add_referral(bot_id, referred_user_id, referrer_user_id):
    """Record a referral relationship."""
    try:
        # Check if already referred to prevent duplicate counts
        exist = await db.referrals.find_one({"bot_id": int(bot_id), "referred_user_id": int(referred_user_id)})
        if exist:
            return False
        
        await db.referrals.insert_one({
            "bot_id": int(bot_id),
            "referred_user_id": int(referred_user_id),
            "referrer_user_id": int(referrer_user_id),
            "referred_at": time.time()
        })
        return True
    except Exception as e:
        logger.error(f"Error adding referral: {e}")
        return False

async def get_referrer(bot_id, referred_user_id):
    """Get the referrer of a user."""
    try:
        res = await db.referrals.find_one({"bot_id": int(bot_id), "referred_user_id": int(referred_user_id)})
        return res.get("referrer_user_id") if res else None
    except Exception as e:
        logger.error(f"Error getting referrer: {e}")
        return None

async def track_click(bot_id, referred_user_id, file_id):
    """Track a unique link click by a referred user."""
    try:
        referrer_id = await get_referrer(bot_id, referred_user_id)
        if not referrer_id:
            return False  # Not a referred user
        
        # Check if this specific referred user already clicked this specific file
        click_id = f"{bot_id}_{referrer_id}_{referred_user_id}_{file_id}"
        exist = await db.referral_clicks.find_one({"_id": click_id})
        if exist:
            return False  # Already counted this click
        
        await db.referral_clicks.insert_one({
            "_id": click_id,
            "bot_id": int(bot_id),
            "referrer_id": int(referrer_id),
            "referred_user_id": int(referred_user_id),
            "file_id": str(file_id),
            "clicked_at": time.time()
        })
        return True
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return False

async def get_leaderboard(bot_id):
    """Retrieve campaign leaderboard sorted by referrals and unique link clicks."""
    try:
        # Get all referrers and count their referrals
        referrals_cursor = db.referrals.aggregate([
            {"$match": {"bot_id": int(bot_id)}},
            {"$group": {"_id": "$referrer_user_id", "referral_count": {"$sum": 1}}},
            {"$sort": {"referral_count": -1}}
        ])
        referrals = [r async for r in referrals_cursor]
        
        # Get all unique clicks counts per referrer
        clicks_cursor = db.referral_clicks.aggregate([
            {"$match": {"bot_id": int(bot_id)}},
            {"$group": {"_id": "$referrer_id", "clicks_count": {"$sum": 1}}}
        ])
        clicks = {c["_id"]: c["clicks_count"] async for c in clicks_cursor}
        
        leaderboard = []
        for r in referrals:
            ref_id = r["_id"]
            leaderboard.append({
                "user_id": ref_id,
                "referral_count": r["referral_count"],
                "clicks_count": clicks.get(ref_id, 0)
            })
            
        return leaderboard
    except Exception as e:
        logger.error(f"Error building leaderboard: {e}")
        return []
