import os
import requests
import re

API_KEY = os.environ["YOUTUBE_API_KEY"]
CHANNEL_ID = "UCcvVw_7dcvSsiJbJqzVCmsg"
HTML_FILE = "media.html"
MAX_VIDEOS = 6


def fetch_latest_videos():
    # Get uploads playlist
    channel_url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?part=contentDetails&id={CHANNEL_ID}&key={API_KEY}"
    )
    uploads_id = requests.get(channel_url).json()[
        "items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Get latest uploads (videos + shorts)
    playlist_url = (
        "https://www.googleapis.com/youtube/v3/playlistItems"
        f"?part=snippet&playlistId={uploads_id}&maxResults={MAX_VIDEOS}&key={API_KEY}"
    )

    data = requests.get(playlist_url).json()
    return [
        (
            item["snippet"]["resourceId"]["videoId"],
            item["snippet"]["title"]
        )
        for item in data.get("items", [])
    ]


def generate_html(videos):
    cards = ""
    for vid, title in videos:
        cards += f"""
        <div class="bg-gray-50 dark:bg-gray-900 rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-all duration-300 w-full max-w-sm">
          <div class="video-container">
            <iframe src="https://www.youtube.com/embed/{vid}" loading="lazy" allowfullscreen></iframe>
          </div>
          <div class="p-4 text-center text-sm font-medium text-gray-700 dark:text-gray-300">
            {title}
          </div>
        </div>
        """

    return f"""
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 px-4 sm:px-10 justify-items-center">
      {cards}
    </div>
    """


def update_html(videos):
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    new_section = generate_html(videos)

    html = re.sub(
        r"<!-- YOUTUBE_SECTION_START -->.*?<!-- YOUTUBE_SECTION_END -->",
        f"<!-- YOUTUBE_SECTION_START -->{new_section}<!-- YOUTUBE_SECTION_END -->",
        html,
        flags=re.DOTALL
    )

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    videos = fetch_latest_videos()
    update_html(videos)
    print("✅ YouTube section updated")
