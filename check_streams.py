import requests

# Add your stream URLs here or load them from your config.json
streams = {
    "CNA": "https://example.com/cna.m3u8",
    "Mewatch": "https://example.com/mewatch.m3u8"
}

def check_health():
    report = "# IPTV Stream Health Report\n\n"
    for name, url in streams.items():
        try:
            # Using a timeout so the script doesn't hang
            response = requests.head(url, timeout=10)
            status = "✅ Online" if response.status_code == 200 else f"❌ Offline (Status: {response.status_code})"
        except Exception as e:
            status = f"⚠️ Error: {str(e)}"
        
        report += f"* **{name}**: {status}\n"
    
    with open("STREAM_STATUS.md", "w") as f:
        f.write(report)

if __name__ == "__main__":
    check_health()
