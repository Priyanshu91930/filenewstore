from flask import Flask, render_template, request, jsonify, send_from_directory
from urllib.parse import unquote
import os, sys

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    """Serve the File Portal website."""
    return send_from_directory('static/website', 'index.html')

@app.route('/tma')
def mini_app():
    """Serve the Telegram Mini App page.

    Query params:
      uid   - Telegram user_id (added by bot when generating the WebApp button)
      token - HMAC-signed verification token (added by bot)
      file  - URL-encoded raw /start parameter (the file data, e.g. base64 file id)
    """
    from config import MONETAG_ZONE_ID, BOT_USERNAME
    from utils import get_tma_shortlink
    import asyncio

    uid          = request.args.get('uid', '')
    token        = request.args.get('token', '')
    file_data    = unquote(request.args.get('file', ''))   # raw /start param
    bot_username = request.args.get('bot', BOT_USERNAME)
    zone         = MONETAG_ZONE_ID or ''

    short_link   = ""
    if uid and token and file_data:
        try:
            # Use a timeout so a slow/blocked shortlink API won't freeze the page
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                short_link = loop.run_until_complete(
                    asyncio.wait_for(
                        get_tma_shortlink(int(uid), token, file_data, bot_username),
                        timeout=4.0   # give up after 4 seconds
                    )
                )
            except asyncio.TimeoutError:
                print("Warning: shortlink generation timed out — using direct bot link fallback")
                short_link = ""
            finally:
                loop.close()
        except Exception as e:
            print(f"Error generating shortlink: {e}")

    # Check if user is already TMA-verified
    is_verified = False
    remaining_time = 0
    if uid and token:
        try:
            from utils import check_tma_verification, TMA_TIMEOUT
            import time as _time
            loop2 = asyncio.new_event_loop()
            asyncio.set_event_loop(loop2)
            try:
                is_verified = loop2.run_until_complete(
                    asyncio.wait_for(check_tma_verification(int(uid)), timeout=3.0)
                )
            finally:
                loop2.close()
            if is_verified:
                # Calculate remaining time
                from utils import TMA_VERIFIED
                key = int(uid)
                if key in TMA_VERIFIED:
                    elapsed = _time.time() - TMA_VERIFIED[key]
                    remaining_time = max(0, int(TMA_TIMEOUT - elapsed))
        except Exception as e:
            print(f"Error checking TMA verification: {e}")

    return render_template(
        'index.html',
        monetag_zone_id = zone,
        user_id         = uid,
        token           = token,
        bot_username    = bot_username,
        file_id         = file_data,          # passed to JS for display/share
        file_deeplink   = file_data,          # used to build the bot ?start= link
        short_link      = short_link,
        is_verified     = is_verified,
        remaining_time  = remaining_time,
    )


@app.route('/tma-verify', methods=['POST'])
def tma_verify():
    """
    Called by the Mini App JS after a successful ad view.
    Validates the HMAC token and returns a deeplink that includes the file data
    so the bot can deliver the correct file immediately.
    """
    from config import TMA_SECRET_KEY, BOT_USERNAME
    import hmac as _hmac, hashlib, time as _time

    data     = request.get_json(silent=True) or {}
    uid_str  = str(data.get('uid', ''))
    token    = str(data.get('token', ''))
    file_data = str(data.get('file', ''))   # file /start param forwarded from JS
    bot_username = str(data.get('bot', BOT_USERNAME))

    # ── Validate HMAC token ──
    try:
        ts_str, sig = token.split('-', 1)
        ts = int(ts_str)
        if _time.time() - ts > 600:          # 10-minute window
            return jsonify({'ok': False, 'error': 'expired'}), 400
        raw      = f"{uid_str}:{ts_str}"
        expected = _hmac.new(TMA_SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()[:16]
        if not _hmac.compare_digest(sig, expected):
            return jsonify({'ok': False, 'error': 'invalid'}), 400
    except Exception:
        return jsonify({'ok': False, 'error': 'bad_token'}), 400

    # ── Build deeplink ──
    # If we have the file data, point directly at the file.
    # Otherwise fall back to the TMA verification callback so the bot marks
    # the user as verified and then re-delivers the pending file.
    if file_data:
        deeplink = f"https://t.me/{bot_username}?start={file_data}"
    else:
        deeplink = f"https://t.me/{bot_username}?start=tma-{uid_str}-{token}"

    return jsonify({'ok': True, 'deeplink': deeplink})

if __name__ == "__main__":
    app.run()
