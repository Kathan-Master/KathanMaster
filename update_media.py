import os
import requests
import re

# --- Configuration ---
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCcvVw_7dcvSsiJbJqzVCmsg"  # replace with your own Channel ID
HTML_FILE = "media.html"
MAX_VIDEOS = 6  # 3x2 grid

# --- YouTube Data API URL ---
url = (
    f"https://www.googleapis.com/youtube/v3/search?"
    f"key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults={MAX_VIDEOS}"
)

def fetch_latest_videos():
    """Fetch latest YouTube videos."""
    response = requests.get(url)
    data = response.json()
    videos = []

    for item in data.get("items", []):
        if item["id"].get("videoId"):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            videos.append((video_id, title))
    return videos

def generate_video_html(videos):
    """Generate YouTube grid HTML."""
    video_cards = ""
    for vid, title in videos:
        video_cards += f"""
        <div class="bg-gray-50 dark:bg-gray-900 rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-all duration-300 w-full max-w-sm" data-aos="zoom-in">
            <div class="video-container">
                <iframe class="w-full h-48 rounded-t-xl"
                    src="https://www.youtube.com/embed/{vid}"
                    title="{title}"
                    frameborder="0"
                    allowfullscreen loading="lazy">
                </iframe>
            </div>
            <div class="p-4">
                <p class="text-gray-700 dark:text-gray-300 text-sm font-medium text-center">{title}</p>
            </div>
        </div>
        """
    return video_cards

def update_html(videos):
    """Replace YouTube section in media.html"""
    if not os.path.exists(HTML_FILE):
        print(f"Error: {HTML_FILE} not found.")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    new_video_html = f"""
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 px-4 sm:px-10 justify-items-center">
        {generate_video_html(videos)}
    </div>
    """

    updated_content = re.sub(
        r"<!-- YOUTUBE_SECTION_START -->.*?<!-- YOUTUBE_SECTION_END -->",
        f"<!-- YOUTUBE_SECTION_START -->{new_video_html}<!-- YOUTUBE_SECTION_END -->",
        html_content,
        flags=re.DOTALL
    )

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("✅ YouTube section updated successfully!")

if __name__ == "__main__":
    print("🔄 Fetching latest YouTube videos...")
    videos = fetch_latest_videos()
    if videos:
        update_html(videos)
    else:
        print("⚠️ No videos found or API error.")
