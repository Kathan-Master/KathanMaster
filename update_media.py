import os
import requests
import re

# --- CONFIGURATION ---
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UC90Nzqy5gVLuMgEm7H3b_cA"  # <-- replace with your YouTube channel ID
MAX_RESULTS = 6  # Number of videos to display

# --- FETCH RECENT VIDEOS ---
def fetch_youtube_videos():
    url = (
        f"https://www.googleapis.com/youtube/v3/search?"
        f"key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id"
        f"&order=date&maxResults={MAX_RESULTS}"
    )
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    videos = []

    for item in data.get("items", []):
        if item["id"]["kind"] == "youtube#video":
            videos.append({
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"]
            })

    return videos


# --- GENERATE YOUTUBE HTML CARDS ---
def generate_video_cards(videos):
    return """
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 px-4 sm:px-8 lg:px-12">
    """ + "\n".join(
        f"""
        <div class="overflow-hidden rounded-xl shadow-md hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <iframe class="w-full aspect-video rounded-xl" 
                src="https://www.youtube.com/embed/{v['videoId']}" 
                title="{v['title']}" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
            <p class="mt-3 text-gray-700 dark:text-gray-300 text-sm font-medium">{v['title']}</p>
        </div>
        """
        for v in videos
    ) + "\n</div>"

# --- UPDATE MEDIA.HTML SAFELY ---
def update_media_html(new_html):
    file_path = "media.html"

    # Read existing content
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Check if markers exist; if not, append them at the bottom
    if "<!-- YOUTUBE_SECTION_START -->" not in html_content:
        html_content += "\n<!-- YOUTUBE_SECTION_START -->\n<!-- YOUTUBE_SECTION_END -->\n"

    # Replace only the content between markers
    pattern = re.compile(
        r"(<!-- YOUTUBE_SECTION_START -->)(.*?)(<!-- YOUTUBE_SECTION_END -->)",
        re.DOTALL,
    )
    updated_html = pattern.sub(r"\1\n" + new_html + r"\n\3", html_content)

    # Write the updated file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated_html)

    print("✅ YouTube section updated successfully!")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        print("🎥 Fetching latest YouTube videos...")
        videos = fetch_youtube_videos()
        if not videos:
            print("⚠️ No videos found. Check your channel ID or API key.")
        else:
            print(f"Fetched {len(videos)} videos.")
            new_html = generate_video_cards(videos)
            update_media_html(new_html)
    except Exception as e:
        print("❌ Error updating media:", e)
