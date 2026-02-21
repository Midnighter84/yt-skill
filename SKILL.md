---
name: youtube
description: >
  YouTube skill for downloading audio from YouTube channels or videos.
  Use when asked to download, grab, save, or fetch audio from YouTube channels,
  videos, or playlists. Triggers on phrases like "download audio from YouTube",
  "grab latest videos from channel", "save audio from this YouTube channel",
  "download from my favourite channels", "add channel to favourites",
  or any YouTube channel/video audio retrieval request.
version: 1.1.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - pip
---

# YouTube Skill

Use this skill for YouTube-related tasks. Currently supports audio downloading and favourite channel management.

## Setup (first time only)

Run once to install dependencies:

```
pip install -r <skill_dir>/scripts/requirements.txt
```

---

## Feature: Manage Favourite Channels

Add, list, or remove YouTube channels from a personal favourites list stored at `~/.yt-skill/favourites.txt`.

### Script

```
python3 <skill_dir>/scripts/favourites.py [options]
```

### Options

| Flag | Short | Description |
|------|-------|-------------|
| `--add URL` | `-a` | Add a channel URL to favourites |
| `--list` | `-l` | List all favourite channels |
| `--remove URL` | `-r` | Remove a channel URL from favourites |
| `--file PATH` | `-f` | Custom favourites file path (default: `~/.yt-skill/favourites.txt`) |

### Output format

```
ADDED <url>           # channel was added
ALREADY_EXISTS <url>  # channel was already in favourites
REMOVED <url>         # channel was removed
NOT_FOUND <url>       # channel not found (exit code 1)
```

### Examples

Add a channel to favourites:
```
python3 <skill_dir>/scripts/favourites.py --add https://www.youtube.com/@mkbhd
```

List all favourite channels:
```
python3 <skill_dir>/scripts/favourites.py --list
```

Remove a channel from favourites:
```
python3 <skill_dir>/scripts/favourites.py --remove https://www.youtube.com/@mkbhd
```

---

## Feature: Download Audio

Download audio from the latest N videos of one or more YouTube channels, or from all favourite channels.
Audio files are saved as `<video_id>.m4a` — no re-encoding, native YouTube format.

### Script

```
python3 <skill_dir>/scripts/download.py [options]
```

### Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--channel URL` | `-c` | YouTube channel URL (repeat for multiple) | |
| `--from-favourites` | `-F` | Download from all channels in the favourites file | |
| `--favourites-file PATH` | | Custom favourites file path | `~/.yt-skill/favourites.txt` |
| `--n COUNT` | `-n` | Number of latest videos per channel | `5` |
| `--output DIR` | `-o` | Directory to save audio files | `./audio` |

At least one of `--channel` or `--from-favourites` is required. Both can be combined.

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

Download latest 5 videos from all favourite channels:
```
python3 <skill_dir>/scripts/download.py --from-favourites
```

Download latest 3 videos from favourites plus an extra channel:
```
python3 <skill_dir>/scripts/download.py --from-favourites --channel https://www.youtube.com/@veritasium --n 3
```

### Notes

- Files are keyed by YouTube video ID, so the same video is never downloaded twice
- No ffmpeg required — audio is downloaded in native M4A format from YouTube
- If a channel has fewer than `--n` videos, all available videos are downloaded
