import os
import asyncio
import random
from kick_api import KickAPI # your existing lib

# --- YOUR CUSTOMER LIST ---
# Add new paying customers here. You can add up to 50!
CHANNEL_SLUGS = [
    "Bonus001",      # Your main channel - FREE
    "customer1",     # Example - replace with real name when someone pays
    "customer2",
    # Just keep adding... "NinjaKick", "AbujaGamer", etc.
]

# --- YOUR PROMOS ---
# This promo will show in ALL channels you guard
# You can later make different promos per customer
PROMO_MESSAGES = [
    "🛡️ Chat protected by KickGuard - DM Bonus001 to protect your channel! $15/mo",
    "🥾 Tactical Boots $45 - kickguard-worldwide.com",
    "🦺 Safety Helmets $25 - WhatsApp +234...",
    "🔥 Want 24/7 chat protection? Bonus001 offers KickGuard service!",
]

BAD_WORDS = ["scam", "buy followers", "http://", "https://", "discord.gg"]

async def guard_channel(channel_name):
    print(f"Starting guard for {channel_name}")
    # Your existing guard + promo logic here loops forever
    while True:
        # Promo every 30 mins
        await asyncio.sleep(1800)
        promo = random.choice(PROMO_MESSAGES)
        print(f"[{channel_name}] Sending promo: {promo}")
        # kick_api.send_message(channel_name, promo)

async def main():
    # Run guard for ALL 50 channels at same time
    tasks = [guard_channel(ch) for ch in CHANNEL_SLUGS if ch != "customer1" and ch != "customer2"]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
