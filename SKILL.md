---
name: youtube
description: >
  YouTube skill for downloading audio from YouTube channels or videos.
  Use when asked to download, grab, save, or fetch audio from YouTube channels,
  videos, or playlists. Triggers on phrases like "download audio from YouTube",
  "grab latest videos from channel", "save audio from this YouTube channel",
  or any YouTube channel/video audio retrieval request.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - pip
---

# YouTube Skill

Use this skill for YouTube-related tasks. Currently supports audio downloading.

## Setup (first time only)

Run once to install dependencies:

```
pip install -r <skill_dir>/scripts/requirements.txt
```

---

## Feature: Download Audio

Download audio from the latest N videos of one or more YouTube channels.
Audio files are saved as `<video_id>.m4a` — no re-encoding, native YouTube format.

### Script

```
python3 <skill_dir>/scripts/download.py [options]
```

### Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--channel URL` | `-c` | YouTube channel URL (repeat for multiple) | required |
| `--n COUNT` | `-n` | Number of latest videos per channel | `5` |
| `--output DIR` | `-o` | Directory to save audio files | `./audio` |

### Accepted channel URL formats

- `https://www.youtube.com/@Handle`
- `https://www.youtube.com/channel/UCxxxxxxxxx`
- `https://www.youtube.com/c/ChannelName`

### Output format

Each video prints exactly one line:

```
DOWNLOADED <video_id>   # audio was fetched and saved
SKIPPED <video_id>      # file already exists on disk, skipped
ERROR <video_id> <msg>  # download failed
```

Exit code is `0` on full success, `1` if any video failed.

### Examples

Download latest 5 videos from one channel (default):
```
python3 <skill_dir>/scripts/download.py --channel https://www.youtube.com/@mkbhd
```

Download latest 10 videos from two channels into a custom directory:
```
python3 <skill_dir>/scripts/download.py \
  --channel https://www.youtube.com/@mkbhd \
  --channel https://www.youtube.com/@LinusTechTips \
  --n 10 \
  --output ~/music/youtube
```

### Notes

- Files are keyed by YouTube video ID, so the same video is never downloaded twice
- No ffmpeg required — audio is downloaded in native M4A format from YouTube
- If a channel has fewer than `--n` videos, all available videos are downloaded
