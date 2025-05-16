import os
import requests
import urllib.parse
from datetime import datetime
import re

def sanitize_filename(filename):
    # Define a regular expression pattern to match invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    # Replace invalid characters with an underscore
    sanitized = re.sub(invalid_chars, '_', filename)
    return sanitized

def get_uuid(ign):
    url = f"https://api.mojang.com/users/profiles/minecraft/{ign}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        raw_uuid = data['id']
        return f"{raw_uuid[0:8]}-{raw_uuid[8:12]}-{raw_uuid[12:16]}-{raw_uuid[16:20]}-{raw_uuid[20:]}"
    else:
        print(f"Could not fetch UUID for IGN: {ign}")
        return None

def extract_youtube_info(url):
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    video_id = None
    start_time = 0

    if 'youtube.com' in parsed.netloc:
        if parsed.path.startswith("/watch"):
            video_id = query.get("v", [None])[0]
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/")[1].split("?")[0]
    elif 'youtu.be' in parsed.netloc:
        video_id = parsed.path[1:]

    if 't' in query:
        t = query['t'][0]
        if 'm' in t or 's' in t:
            match = re.match(r'(?:(\d+)m)?(?:(\d+)s)?', t)
            if match:
                minutes = int(match.group(1) or 0)
                seconds = int(match.group(2) or 0)
                start_time = minutes * 60 + seconds
        else:
            start_time = int(t)

    return video_id, start_time

def fetch_youtube_title(video_url):
    api_url = f"https://noembed.com/embed?url={video_url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json().get("title", "YouTube Video")
    else:
        return "YouTube Video"

def format_time(seconds):
    return f"{seconds//60}:{seconds%60:02d}"

def fetch_post_filenames():
    # Fetch filenames from the local _posts directory
    posts_dir = "_posts"
    if os.path.exists(posts_dir):
        return [f for f in os.listdir(posts_dir) if os.path.isfile(os.path.join(posts_dir, f))]
    else:
        print(f"Directory '{posts_dir}' not found.")
        return []

def find_filename_by_uuid(filenames, uuid):
    for name in filenames:
        if uuid in name:
            return name
    return None

def generate_post(video_url, igns, time, role="UNKNOWN", tags=["casual", "legit-run"]):
    uuids = [get_uuid(ign) for ign in igns]
    if role.lower() not in tags:
        tags.append(role.lower())
        
    if None in uuids:
        print("Aborting due to missing UUIDs.")
        return

    video_id, start_time = extract_youtube_info(video_url)
    if not video_id:
        print("Could not extract video ID from the URL.")
        return

    video_title = fetch_youtube_title(video_url)
    title_time = format_time(start_time)
    subtitle = ", ".join(igns)
    tag_str = ", ".join(tags)
    uuid_str = ", ".join(uuids)

    filenames = fetch_post_filenames()
    links = ""

    for ign, uuid in zip(igns, uuids):
        filename = find_filename_by_uuid(filenames, uuid)
        if filename:
            clean_filename = filename[:-3] if filename.endswith(".md") else filename
            links += f"- [{ign}](https://thenose2003.github.io/{clean_filename})\n"
        else:
            # Create player markdown file with today's date and UUID
            today_date = datetime.now().strftime("%Y-%m-%d")
            player_md = f"""---
layout: player
uuid: {uuid}
tags: [player]
---

# Runs
---
"""
            player_filename = f"_posts/{today_date}-{uuid}.md"
            with open(player_filename, "w", encoding="utf-8") as pf:
                pf.write(player_md)
            print(f"Created missing player file: {player_filename}")

            links += f"- [{ign}](https://thenose2003.github.io/{today_date}-{uuid})\n"

    post_md = f"""---
layout: post
title: "[{time}] [{role}] {igns[0]}"
subtitle: {subtitle}
tags: [{tag_str}]
time: {int(time.split(':')[0])*60 + int(time.split(':')[1])}
players: [{uuid_str}]
---

# {video_title}
<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}?start={start_time}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

# Players
{links}
"""

    with open(f"_posts/{datetime.now().strftime('%Y-%m-%d')}-{igns[0]}-{sanitize_filename(video_title)}.md", "w", encoding="utf-8") as f:
        f.write(post_md)

    print(f"Markdown file generated: {datetime.now().strftime('%Y-%m-%d')}-{sanitize_filename(video_title)}")

# Example usage
if __name__ == "__main__":
    time = "5:27"
    role = "Archer" 
    
    # pb-run 
    # tas-run
    # tntpearl
    # casual
    # legit-run

    tags = ["casual", "legit-run"]
    
    youtube_link = "https://www.youtube.com/watch?v=FpjLvQNpbwk"
    igns = ["Nashes", "bruhplane", "FiskeFillet", "Totoki", "Vortie"]
    generate_post(youtube_link, igns, time, role=role, tags=tags)
