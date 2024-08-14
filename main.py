import os

from telethon import TelegramClient, events
from datetime import datetime, timedelta
import re

# Replace with your own credentials
bot_token = '7077890021:AAG-rsFpkYQb8KnKjE6zUspHP6mhFI_sUvM'
api_id = '20588411'  # Replace with your API ID
api_hash = '93edc28575ad46194e94f4a5997c5a02'  # Replace with your API Hash
source_channel_username = '@DSNewPairsSolana'  # Source channel username or ID
target_channel_username = '@cpmmdex'  # Target channel username or ID

# Patterns to filter out (adjust the patterns as needed)
filter_patterns = [r'.pump.', 'meteora', 'orca', r'.*pattern.']

client = TelegramClient('session_name', api_id, api_hash)

def filter_message(message_text):
    """
    Filters messages based on specific patterns, liquidity value, and FDV.
    Returns True if the message should be sent, False otherwise.
    """
    # Convert message text to lowercase for case-insensitive matching
    message_text = message_text.lower()

    # Check if the message matches any of the filter patterns
    if any(re.search(pattern, message_text) for pattern in filter_patterns):
        return False  # Skip this message

    # Check if the message contains "Total liquidity:" and the value is greater than 10,000
    liquidity_match = re.search(r'total liquidity:\s*\*\*\s*\$\s*([\d,]+)\s*\*\*', message_text)
    if liquidity_match:
        liquidity_value = int(liquidity_match.group(1).replace(',', ''))
        if liquidity_value <= 10000:
            return False  # Skip this message

    # Check if the message contains "FDV:" and the value is greater than 500,000
    fdv_match = re.search(r'fdv:\s*\*\*\s*\$\s*([\d,]+)\s*\*\*', message_text)
    if fdv_match:
        fdv_value = int(fdv_match.group(1).replace(',', ''))
        if not (500000 <= fdv_value <= 2000000):
            return False  # Skip this message

    return True  # Message passed all filters

@client.on(events.NewMessage(chats=source_channel_username))
async def handler(event):
    message = event.message

    if filter_message(message.text):
        await client.send_message(target_channel_username, message.text)

async def main():
    await client.start()

    # Fetch messages from the last 30 minutes initially
    thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
    messages = await client.get_messages(source_channel_username, offset_date=thirty_minutes_ago)

    for message in messages:
        if filter_message(message.text):
            await client.send_message(target_channel_username, message.text)

    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())