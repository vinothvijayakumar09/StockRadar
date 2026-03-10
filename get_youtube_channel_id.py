#!/usr/bin/env python3
"""
Helper script to get YouTube Channel ID from handle
Usage: python get_youtube_channel_id.py @berich467
"""

import requests
import re
import sys

def get_channel_id(handle: str) -> str:
    """Extract YouTube channel ID from handle"""
    # Remove @ if present
    handle = handle.lstrip('@')
    
    # Try the new handle format
    url = f"https://www.youtube.com/@{handle}"
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Search for channel ID in the page source
        # Pattern 1: channelId in meta tags or scripts
        pattern1 = r'"channelId":"([^"]+)"'
        match = re.search(pattern1, response.text)
        
        if match:
            channel_id = match.group(1)
            print(f"\n✅ Channel ID found: {channel_id}")
            print(f"\nAdd this to your .env file:")
            print(f"YOUTUBE_CHANNEL_ID={channel_id}")
            print(f"\nRSS Feed URL:")
            print(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
            return channel_id
        
        # Pattern 2: Alternative format
        pattern2 = r'browseId":"([^"]+)"'
        match = re.search(pattern2, response.text)
        
        if match:
            channel_id = match.group(1)
            print(f"\n✅ Channel ID found: {channel_id}")
            print(f"\nAdd this to your .env file:")
            print(f"YOUTUBE_CHANNEL_ID={channel_id}")
            print(f"\nRSS Feed URL:")
            print(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
            return channel_id
        
        print("❌ Could not find channel ID in page source")
        print("Try visiting the channel page and checking the source code manually")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nManual method:")
        print(f"1. Visit https://www.youtube.com/@{handle}")
        print(f"2. View page source (Ctrl/Cmd+U)")
        print(f"3. Search for 'channelId' or 'browseId'")
        print(f"4. Copy the ID and add to .env file")
    
    return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_youtube_channel_id.py @berich467")
        sys.exit(1)
    
    handle = sys.argv[1]
    get_channel_id(handle)
