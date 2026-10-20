import os
import time
import requests
import re
from datetime import datetime

# === CONFIG ===
KICK_TOKEN = os.getenv("KICK_TOKEN", "").strip()
CHANNEL_SLUG = os.getenv("CHANNEL_SLUG", "Bonus001").strip()

# Bad words list - add more later
BAD_WORDS = ["fuck", "nigger", "scam", "buy followers", "http://", "https://", "discord.gg"]
TIMEOUT_SECONDS = 300

API_BASE = "https://kick.com/api/v2"
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

def contains_bad(text):
    low = text.lower()
    for w in BAD_WORDS:
        if w.lower() in low:
            return w
    return None

def run():
    if not KICK_TOKEN:
        log("ERROR: KICK_TOKEN not set! Add it in hosting dashboard.")
        while True:
            time.sleep(60)
            
    log(f" KickGuard GLOBAL starting for channel: {CHANNEL_SLUG}")
    channel_id = get_channel_id()
    if not channel_id:
        log(f"Could not find channel {CHANNEL_SLUG}, trying chat loop anyway...")
        channel_id = 1
        
    seen_ids = set()
    log(" Bot is LIVE and protecting chat...")
    
    while True:
        try:
            messages = get_chat_messages(channel_id)
            # Kick returns newest first
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
                    log(f" SPAM DETECTED from {username}: '{content[:50]}' -> word: {bad}")
                    if delete_message(mid):
                        log(f"  -> Deleted")
                    if user_id:
                        ban_user(user_id)
                        log(f"  -> Timed out {username} for {TIMEOUT_SECONDS}s")
                        
            time.sleep(2)
        except Exception as e:
            log(f"Loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run()
