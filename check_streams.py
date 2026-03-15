import os
import requests
import re
from datetime import datetime

# 1. Securely get the Dropbox URL from GitHub Secrets
DROPBOX_M3U_URL = os.environ.get('MY_DROPBOX_URL')

def get_m3u_channels():
    if not DROPBOX_M3U_URL:
        print("❌ Error: MY_DROPBOX_URL secret not found.")
        return []
    
    try:
        print("Fetching playlist from Dropbox...")
        # Adding a header to the request to ensure Dropbox doesn't block the download
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(DROPBOX_M3U_URL, timeout=15, headers=headers)
        response.raise_for_status()
        content = response.text
        
        # Regex to find Channel Name and URL (Supports .m3u8, .mpd, .ts, etc.)
        pattern = r'#EXTINF:.*?,(.*?)\n(http[s]?://.*)'
        matches = re.findall(pattern, content)
        
        print(f"Found {len(matches)} channels.")
        return matches 
    except Exception as e:
        print(f"❌ Error fetching M3U: {e}")
        return []

def check_health():
    channels = get_m3u_channels()
    if not channels:
        return

    # Create the report header
    report = f"# 📺 IPTV Health Report\n"
    report += f"**Last Checked:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (SGT)\n\n"
    report += "| Channel Name | Status | Type | Result |\n"
    report += "| :--- | :--- | :--- | :--- |\n"

    # Browser-like headers to prevent 403 Forbidden errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for name, url in channels:
        name = name.strip()
        url = url.strip()
        
        # Identify stream type for the report
        stream_type = "DASH (.mpd)" if ".mpd" in url.lower() else "HLS (.m3u8)"
        
        try:
            # We use stream=True to check the connection without downloading the video data
            resp = requests.get(url, timeout=10, stream=True, headers=headers)
            if resp.status_code == 200:
                status = "✅ Online"
                result = "200 OK"
            else:
                status = "❌ Offline"
                result = f"Error {resp.status_code}"
        except Exception as e:
            status = "⚠️ Failed"
            result = "Timeout/Error"
        
        report += f"| {name} | {status} | {stream_type} | {result} |\n"

    # Save the final report to your GitHub repo
    with open("STREAM_STATUS.md", "w") as f:
        f.write(report)
    print("Success: STREAM_STATUS.md generated.")

if __name__ == "__main__":
    check_health()
