import os
import requests
import re
from datetime import datetime

# 1. Securely fetch the Dropbox URL from GitHub Secrets
DROPBOX_M3U_URL = os.environ.get('MY_DROPBOX_URL')

def get_m3u_channels():
    if not DROPBOX_M3U_URL:
        print("❌ Error: MY_DROPBOX_URL secret not found.")
        return []
    
    try:
        print("Fetching playlist from Dropbox...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(DROPBOX_M3U_URL, timeout=15, headers=headers)
        response.raise_for_status()
        
        lines = response.text.splitlines()
        channels = []
        
        # We loop through the file to find #EXTINF and then 'look ahead' for the URL
        for i in range(len(lines)):
            line = lines[i].strip()
            
            if line.startswith("#EXTINF:"):
                # Extract channel name (everything after the last comma)
                name_match = re.search(r',([^,]*)$', line)
                name = name_match.group(1).strip() if name_match else "Unknown Channel"
                
                # LOOK AHEAD: Skip #KODIPROP and other tags to find the HTTP link
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line.startswith("http"):
                        channels.append((name, next_line))
                        break # Found the URL, stop looking for this specific channel
                    elif next_line.startswith("#EXTINF:"):
                        break # Hit the next channel without finding a URL (malformed M3U)
        
        print(f"✅ Successfully parsed {len(channels)} channels.")
        return channels 
    except Exception as e:
        print(f"❌ Error fetching M3U: {e}")
        return []

def check_health():
    channels = get_m3u_channels()
    if not channels:
        print("No channels found.")
        return

    # Create the report header
    report = f"# 📺 IPTV Health Report\n"
    report += f"**Last Checked:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (SGT)\n\n"
    report += "| Channel Name | Status | Type | Result |\n"
    report += "| :--- | :--- | :--- | :--- |\n"

    # Mimic a real browser so servers don't reject the 'ping'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

    for name, url in channels:
        stream_type = "DASH (.mpd)" if ".mpd" in url.lower() else "HLS (.m3u8)"
        
        try:
            # We use stream=True to check connectivity without downloading the video
            resp = requests.get(url, timeout=10, stream=True, headers=headers, allow_redirects=True)
            
            if resp.status_code == 200:
                status = "✅ Online"
                result = "200 OK"
            elif resp.status_code == 403:
                status = "⚠️ Restricted"
                result = "403 (Requires Key/Token)"
            else:
                status = "❌ Offline"
                result = f"Error {resp.status_code}"
        except Exception as e:
            status = "❌ Failed"
            result = "Timeout/Down"
        
        report += f"| {name} | {status} | {stream_type} | {result} |\n"

    # Save the status report to the repository
    with open("STREAM_STATUS.md", "w") as f:
        f.write(report)
    print("Success: STREAM_STATUS.md updated.")

if __name__ == "__main__":
    check_health()
