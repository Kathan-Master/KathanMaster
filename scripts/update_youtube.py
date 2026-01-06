import os
import requests
import re

API_KEY = os.environ["YOUTUBE_API_KEY"]
HTML_FILE = "media.html"
MAX_VIDEOS = 30   # fetch more so loop looks smooth


def fetch_latest_videos():
    CHANNEL_HANDLE = "@kathanmaster"

    # 1. Get uploads playlist
    channel_url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
    )

    channel_data = requests.get(channel_url).json()
    if not channel_data.get("items"):
        raise RuntimeError("Channel not found or API error")

    uploads_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # 2. Fetch uploads
    playlist_url = (
        "https://www.googleapis.com/youtube/v3/playlistItems"
        f"?part=snippet&playlistId={uploads_id}&maxResults=50&key={API_KEY}"
    )

    playlist_data = requests.get(playlist_url).json()

    video_ids = [
        item["snippet"]["resourceId"]["videoId"]
        for item in playlist_data.get("items", [])
    ]

    # 3. Fetch durations
    videos_url = (
        "https://www.googleapis.com/youtube/v3/videos"
        f"?part=contentDetails&id={','.join(video_ids)}&key={API_KEY}"
    )

    duration_data = requests.get(videos_url).json()
    duration_map = {
        item["id"]: item["contentDetails"]["duration"]
        for item in duration_data.get("items", [])
    }

    # 4. Mix long videos + shorts
    longs, shorts = [], []

    for item in playlist_data.get("items", []):
        vid = item["snippet"]["resourceId"]["videoId"]
        title = item["snippet"]["title"]
        duration = duration_map.get(vid, "")

        if "M" in duration:
            longs.append((vid, title))
        else:
            shorts.append((vid, title))

    mixed = []
    while longs or shorts:
        if longs:
            mixed.append(longs.pop(0))
        if shorts:
            mixed.append(shorts.pop(0))

    return mixed[:MAX_VIDEOS]


def generate_html(videos):
    cards = ""

    for vid, title in videos:
        cards += f"""
        <div class="youtube-card">
          <div class="video-container">
            <iframe src="https://www.youtube.com/embed/{vid}"
                    loading="lazy" allowfullscreen></iframe>
          </div>
          <p class="yt-title">{title}</p>
        </div>
        """

    count = len(videos)

    # duplicate for loop
    cards = cards + cards

    return f"""
    <div class="yt-scroll-wrapper">
      <div class="yt-scroll-track" style="--card-count:{count}">
        {cards}
      </div>
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
