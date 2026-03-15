import os
import requests
import re
from datetime import datetime

# This looks for the secret you saved in GitHub Settings
DROPBOX_M3U_URL = os.environ.get('MY_DROPBOX_URL')

def get_m3u_channels():
    if not DROPBOX_M3U_URL:
        print("❌ Error: MY_DROPBOX_URL secret not found in GitHub Settings.")
        return []
    
    try:
        print("Fetching playlist from Dropbox...")
        response = requests.get(DROPBOX_M3U_URL, timeout=15)
        response.raise_for_status()
        content = response.text
        
        # This finds the channel name and the URL in your M3U
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

    # Create the header for your status file
    report = f"# 📺 IPTV Health Report\n"
    report += f"**Last Checked:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (SGT)\n\n"
    report += "| Channel Name | Status | Last Result |\n"
    report += "| :--- | :--- | :--- |\n"

    for name, url in channels:
        name = name.strip()
        url = url.strip()
        try:
            # We use a 'get' with a small stream=True to verify the link actually works
            # without downloading the whole video stream.
            resp = requests.get(url, timeout=10, stream=True)
            if resp.status_code == 200:
                status = "✅ Online"
                result = "200 OK"
            else:
                status = "❌ Offline"
                result = f"Error {resp.status_code}"
        except Exception as e:
            status = "⚠️ Failed"
            result = "Connection Timeout"
        
        report += f"| {name} | {status} | {result} |\n"

    # Save the report as a Markdown file in your repo
    with open("STREAM_STATUS.md", "w") as f:
        f.write(report)
    print("Report generated: STREAM_STATUS.md")

if __name__ == "__main__":
    check_health()
