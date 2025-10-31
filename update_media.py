import os
import requests
from html import escape

# --- CONFIGURATION ---
# Get the API Key from GitHub Secrets (Environment Variable)
API_KEY = os.environ.get('YOUTUBE_API_KEY')
# Your Channel ID copied in Step 2
CHANNEL_ID = 'UC90Nzqy5gVLuMgEm7H3b_cA' 
MAX_VIDEOS = 6  # Number of recent videos to display
MEDIA_HTML_FILE = 'media.html'
# --- END CONFIGURATION ---

def get_latest_youtube_videos(channel_id, api_key, max_results):
    """Fetches the latest videos from a YouTube channel using the API."""
    try:
        # 1. Get the Channel's Uploads Playlist ID (a playlist automatically created by YouTube)
        channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
        response = requests.get(channel_url).json()
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # 2. Get the latest videos from the Uploads Playlist
        playlist_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist_id}&key={api_key}&maxResults={max_results}"
        response = requests.get(playlist_url).json()
        
        videos = []
        for item in response.get('items', []):
            snippet = item['snippet']
            videos.append({
                'title': escape(snippet['title']),
                'video_id': snippet['resourceId']['videoId']
            })
        return videos
    
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")
        return []

def generate_video_html(videos):
    """Generates the HTML grid for the latest videos."""
    html_content = ""
    for video in videos:
        # Construct the YouTube embed URL
        embed_url = f"https://www.youtube.com/embed/{video['video_id']}?controls=0"
        
        # HTML structure for one video card (using your existing Tailwind structure)
        card = f"""
                <div class="media-card" data-aos="zoom-in">
                    <div class="video-container mb-3">
                        <iframe width="560" height="315" 
                                src="{embed_url}" 
                                title="YouTube video player: {video['title']}" 
                                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                                referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
                        </iframe>
                    </div>
                    <h3 class="font-semibold mb-2">{video['title']}</h3>
                </div>
        """
        html_content += card
        
    return f'<div class="grid grid-cols-1 md:grid-cols-3 gap-6">\n{html_content}\n</div>'

def update_html_file(new_html, file_path):
    """Reads the HTML file, replaces content between markers, and saves it."""
    # Define markers for where the automated content goes
    START_MARKER = ""
    END_MARKER = ""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        start_index = content.find(START_MARKER)
        end_index = content.find(END_MARKER)

        if start_index == -1 or end_index == -1:
            print(f"Error: Automation markers not found in {file_path}")
            return False

        # Build the new content block
        new_content_block = f"{START_MARKER}\n{new_html}\n\t\t\t\t{END_MARKER}"
        
        # Replace the old content between the markers
        updated_content = content[:start_index] + new_content_block + content[end_index + len(END_MARKER):]

        with open(file_path, 'w') as f:
            f.write(updated_content)
        
        print(f"Successfully updated {file_path} with {len(videos)} videos.")
        return True

    except Exception as e:
        print(f"Error updating HTML file: {e}")
        return False


if __name__ == '__main__':
    # 1. Fetch data
    videos = get_latest_youtube_videos(CHANNEL_ID, API_KEY, MAX_VIDEOS)
    
    if videos:
        # 2. Generate HTML
        new_html_content = generate_video_html(videos)
        
        # 3. Update HTML file
        update_html_file(new_html_content, MEDIA_HTML_FILE)
    else:
        print("No videos fetched. Skipping HTML update.")
