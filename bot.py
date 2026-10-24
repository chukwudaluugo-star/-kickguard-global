import os
import time
import requests
import random
from datetime import datetime

# === CONFIG ===
KICK_TOKEN = os.getenv("KICK_TOKEN", "").strip()
CHANNEL_SLUG = os.getenv("CHANNEL_SLUG", "Bonus001").strip()

BAD_WORDS = ["fuck", "nigger", "scam", "buy followers", "http://", "https://", "discord.gg"]
TIMEOUT_SECONDS = 300
API_BASE = "https://kick.com/api/v2"

# Different promo messages - bot picks random one
PROMO_MESSAGES = [
    "🛡️ KickGuard Safety! Tactical Boots $45 - kickguard-worldwide.onrender.com",
    "👷 Safety Helmets $25 + Gloves $15 - Worldwide Shipping! !shop",
    "🔥 Steel Toe Boots $55 - DM Bonus001 on WhatsApp +1 289 793-0481",
    "⚡ High-Vis Vest $18 - Protecting Your World, One Gear at a Time!",
    "💪 Work Coveralls $40 - Trusted by USA & Nigeria workers!"
]

AUTH_HEADER = {"Authorization": f"Bearer {KICK_TOKEN}", "Content-Type": "application/json"}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_channel_id():
    try:
        r = requests.get(f"{API_BASE}/channels/{CHANNEL_SLUG}", timeout=10)
        if r.status_code == 200:
            return r.json().get("id")
    except Exception as e:
        log(f"Channel lookup error: {e}")
    return None

def get_chat_messages(channel_id):
    try:
        r = requests.get(f"{API_BASE}/channels/{channel_id}/messages", headers=AUTH_HEADER, timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def delete_message(message_id):
    try:
        r = requests.delete(f"{API_BASE}/messages/{message_id}", headers=AUTH_HEADER, timeout=10)
        return r.status_code in [200,204]
    except:
        return False

def ban_user(user_id, duration=TIMEOUT_SECONDS):
    try:
        data = {"user_id": user_id, "duration": duration, "reason": "KickGuard auto-mod"}
        r = requests.post(f"{API_BASE}/moderation/bans", headers=AUTH_HEADER, json=data, timeout=10)
        return r.status_code in [200,201,204]
    except Exception as e:
        log(f"Ban error: {e}")
        return False

def send_chat_message(channel_id, text):
    try:
        data = {"content": text, "type": "message"}
        r = requests.post(f"{API_BASE}/channels/{channel_id}/chat", headers=AUTH_HEADER, json=data, timeout=10)
        if r.status_code in [200,201]:
            log(f"✅ PROMO SENT: {text}")
            return True
        else:
            log(f"Promo failed: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        log(f"Send error: {e}")
    return False

def contains_bad(text):
    low = text.lower()
    for w in BAD_WORDS:
        if w.lower() in low:
            return w
    return None

def run():
    if not KICK_TOKEN:
        log("ERROR: KICK_TOKEN not set! Add it in Render > Environment")
        while True:
            time.sleep(60)

    log(f"KickGuard GLOBAL starting for channel: {CHANNEL_SLUG}")
    channel_id = get_channel_id()
    if not channel_id:
        log(f"Could not find channel {CHANNEL_SLUG}, using ID 1")
        channel_id = 1

    seen_ids = set()
    last_promo = time.time()
    log("Bot is LIVE - Guarding + Promo every 30 mins...")

    while True:
        try:
            # PROMO EVERY 30 MINS = 1800 seconds
            if time.time() - last_promo > 1800:
                promo = random.choice(PROMO_MESSAGES)
                send_chat_message(channel_id, promo)
                last_promo = time.time()

            messages = get_chat_messages(channel_id)
            for msg in reversed(messages if isinstance(messages, list) else []):
                mid = str(msg.get("id", ""))
                if mid in seen_ids:
                    continue
                seen_ids.add(mid)
                if len(seen_ids) > 500:
                    seen_ids.clear()

                content = msg.get("content", "") or msg.get("message", "") or ""
                username = msg.get("sender", {}).get("username", "unknown")
                user_id = msg.get("sender", {}).get("id")
                bad = contains_bad(content)
                if bad:
                    log(f"SPAM from {username}: '{content[:50]}' -> {bad}")
                    if delete_message(mid):
                        log(f" -> Deleted")
                    if user_id:
                        ban_user(user_id)
                        log(f" -> Timed out {username}")

            time.sleep(5)
        except Exception as e:
            log(f"Loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run()
