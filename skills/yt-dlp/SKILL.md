---
name: yt-dlp
description: Download audio/video from YouTube and 1000+ sites with yt-dlp. Extract metadata, convert formats, download subtitles, and more.
metadata:
  openclaw:
    requires:
      bins: [yt-dlp]
    install:
      - id: pip
        kind: python
        package: yt-dlp
---

# yt-dlp Skill

A powerful audio/video downloader with support for 1000+ sites.

## Installation

```bash
# Install via pip
pip install yt-dlp

# Or use standalone binary
brew install yt-dlp  # macOS
```

## Usage

### Basic Download

```bash
# Download video
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID"

# Download audio only (MP3)
yt-dlp -x --audio-format mp3 "https://www.youtube.com/watch?v=VIDEO_ID"

# Download playlist
yt-dlp "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Format Options

```bash
# Download best quality
yt-dlp -f best "https://www.youtube.com/watch?v=VIDEO_ID"

# Download worst quality (smaller file)
yt-dlp -f worst "https://www.youtube.com/watch?v=VIDEO_ID"

# Download specific quality (1080p)
yt-dlp -f "bestvideo[height<=1080]+bestaudio" "https://www.youtube.com/watch?v=VIDEO_ID"

# Download audio only
yt-dlp -x --audio-format mp3 "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Subtitle Options

```bash
# Download subtitles
yt-dlp --write-subs "https://www.youtube.com/watch?v=VIDEO_ID"

# Download all subtitles
yt-dlp --all-subs "https://www.youtube.com/watch?v=VIDEO_ID"

# Download English subtitles only
yt-dlp --subs-lang en "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Output Options

```bash
# Custom output filename
yt-dlp -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"

# Download to specific directory
yt-dlp -o "/path/to/downloads/%(title)s.%(ext)s" "URL"

# Numbered playlist files
yt-dlp -o "%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"
```

### Common Options

```bash
# Verbose output
yt-dlp -v "https://www.youtube.com/watch?v=VIDEO_ID"

# Download thumbnail/cover art
yt-dlp --embed-thumbnail "https://www.youtube.com/watch?v=VIDEO_ID"

# Add metadata to file
--embed-metadata "https://www.youtube.com/watch?v=VIDEO_ID"

# Skip already downloaded files
-c --continue  # Resume partial downloads
--download-archive archive.txt  # Skip already downloaded
```

### Authentication

```bash
# Login with cookies
--cookies cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID"

# Use netrc for authentication
# Create ~/.netrc file with:
#   machine youtube login EMAIL password APP_PASSWORD
#   machine twitch login EMAIL password APP_PASSWORD
--netrc "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Playlist Options

```bash
# Download full playlist
yt-dlp "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Download first 10 videos from playlist
yt-dlp --playlist-items 1-10 "PLAYLIST_URL"

# Download specific videos
yt-dlp --playlist-items 1,3,5 "PLAYLIST_URL"

# Download entire channel
yt-dlp "https://www.youtube.com/@CHANNEL_NAME/videos"
```

### Post-Processing

```bash
# Extract audio (after video download)
-x --postprocessor-args "-ss 00:00:30 -t 00:03:00" "URL"

# Trim video
--postprocessor-args "ffmpeg;-i;$FILE;-ss;30;-to;180;-c;copy" "URL"

# Merge video + audio
--merge-output-format mkv "URL"
```

## Common Use Cases

### YouTube

```bash
# Best quality + thumbnails + metadata
yt-dlp -f best -ciw --embed-thumbnail --add-metadata "https://youtu.be/VIDEO_ID"

# Download playlist as MP3
yt-dlp -x --audio-format mp3 -o "%(playlist)s/%(title)s.%(ext)s" "PLAYLIST_URL"

# Download age-restricted video (need cookies)
--cookies cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Audio Extraction

```bash
# Podcast to MP3
yt-dlp -x --audio-format mp3 --audio-quality 0 "https://podcast.com/episode"

# Music album from SoundCloud
yt-dlp -x --audio-format flac "https://soundcloud.com/artist/album"
```

### Live Streams

```bash
# Download live stream (will keep recording until ended)
yt-dlp "https://www.youtube.com/watch?v=LIVE_ID"

# Record and split by chapters
yt-dlp --embed-chapters "https://www.youtube.com/watch?v=LIVE_ID"
```

### Course Platforms

```bash
# Udemy (requires login)
--cookies cookies.txt "https://www.udemy.com/course-name"

# Coursera (requires login)
--cookies cookies.txt "https://www.coursera.org/learn/course-name"
```

### Social Media

```bash
# Twitter/X video
yt-dlp "https://twitter.com/user/status/ID"

# Instagram post
yt-dlp "https://www.instagram.com/p/POST_ID"

# TikTok
yt-dlp "https://www.tiktok.com/@user/video/ID"

# Bilibili
yt-dlp "https://www.bilibili.com/video/BV1XXX"
```

## OpenClaw Integration

### Script Example

```python
#!/usr/bin/env python3
"""YouTube Downloader using yt-dlp"""

import subprocess
import json
from pathlib import Path
from typing import Optional

def get_video_info(url: str) -> dict:
    """Get video metadata without downloading"""
    result = subprocess.run(
        ["yt-dlp", "--dump-json", url],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def download_audio(url: str, output_dir: str = "downloads") -> str:
    """Download audio as MP3"""
    Path(output_dir).mkdir(exist_ok=True)
    result = subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3", 
         "-o", f"{output_dir}/%(title)s.%(ext)s",
         url],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def download_playlist(url: str, output_dir: str = "playlist") -> str:
    """Download playlist"""
    Path(output_dir).mkdir(exist_ok=True)
    result = subprocess.run(
        ["yt-dlp", "-o", f"{output_dir}/%(playlist_index)s - %(title)s.%(ext)s",
         "--yes-playlist", url],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

if __name__ == "__main__":
    info = get_video_info("https://www.youtube.com/watch?v=VIDEO_ID")
    print(f"Title: {info['title']}")
    print(f"Duration: {info['duration']}s")
    print(f"Formats: {len(info['formats'])}")
```

## Supported Sites

yt-dlp supports 1000+ sites including:

- **Video**: YouTube, Vimeo, Dailymotion, Bilibili, NicoNico, TikTok, Twitter/X
- **Audio**: SoundCloud, Bandcamp, Spotify, Apple Music
- **Live**: Twitch, YouTube Live, Kick
- **Social**: Instagram, Reddit, Tumblr
- **Educational**: Udemy, Coursera, LinkedIn Learning
- **News**: CNN, BBC, FOX

Full list: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## Troubleshooting

### Slow Downloads

```bash
# Use faster downloader (aria2c)
--external-downloader aria2c --external-downloader-args "-x 16 -s 16" "URL"

# Limit download speed
--limit-rate 5M "URL"
```

### Geo-Restricted Content

```bash
# Use proxy
--proxy "http://PROXY:PORT" "URL"

# Bypass region lock (if available)
--geo-bypass "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Cookies Issues

```bash
# Export cookies from browser
--cookies-from-browser chrome "https://www.youtube.com/watch?v=VIDEO_ID"

# Or export manually using extensions like "Get cookies.txt"
```

### Format Not Available

```bash
# List available formats
yt-dlp -F "https://www.youtube.com/watch?v=VIDEO_ID"

# Force specific format
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" "URL"
```

## Tips

1. **Always check available formats** first:
   ```bash
   yt-dlp -F "URL" | head -20
   ```

2. **Use cookies for age-restricted content**:
   ```bash
   --cookies cookies.txt "URL"
   ```

3. **Resume interrupted downloads**:
   ```bash
   yt-dlp -c "URL"
   ```

4. **Batch download from file**:
   ```bash
   yt-dlp -a urls.txt
   ```

5. **Skip duplicates**:
   ```bash
   --download-archive archive.txt "URL"
   ```

## Resources

- GitHub: https://github.com/yt-dlp/yt-dlp
- Wiki: https://github.com/yt-dlp/yt-dlp/wiki
- FAQ: https://github.com/yt-dlp/yt-dlp/wiki/FAQ
- Discord: https://discord.gg/H5MNcFW63r
