import requests
import re

# Replace this with your actual Dropbox "Direct Download" link
DROPBOX_M3U_URL = "https://www.dropbox.com/s/mmzlpr945rvpjb8/KTVMate.m3u?dl=1"

def get_m3u_channels():
    try:
        response = requests.get(DROPBOX_M3U_URL, timeout=15)
        response.raise_for_status()
        content = response.text
        
        # Regex to find #EXTINF (Name) and the URL immediately following it
        # This matches: #EXTINF:-1...,Channel Name \n http://...
        pattern = r'#EXTINF:.*?,(.*?)\n(http[s]?://.*)'
        matches = re.findall(pattern, content)
        
        return matches # Returns a list of tuples: [('Channel Name', 'URL'), ...]
    except Exception as e:
        print(f"Error fetching M3U: {e}")
        return []

def check_health():
    channels = get_m3u_channels()
    if not channels:
        return

    report = f"# IPTV Health Report (Synced from Dropbox)\n"
    report += f"Last Checked: {requests.utils.quote(str(requests.utils.datetime.datetime.now()))}\n\n"

    for name, url in channels:
        name = name.strip()
        url = url.strip()
        try:
            # We use a HEAD request to save bandwidth
            resp = requests.head(url, timeout=5, allow_redirects=True)
            status = "✅ Online" if resp.status_code == 200 else f"❌ Offline ({resp.status_code})"
        except:
            status = "⚠️ Connection Failed"
        
        report += f"* **{name}**: {status}\n"

    with open("STREAM_STATUS.md", "w") as f:
        f.write(report)

if __name__ == "__main__":
    check_health()
