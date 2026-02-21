---
name: youtube
description: >
  YouTube skill for downloading audio from YouTube channels or videos and
  transcribing them with Whisper. Use when asked to download, grab, save,
  fetch, or transcribe audio from YouTube channels, videos, or playlists.
  Triggers on phrases like "download audio from YouTube", "grab latest videos
  from channel", "save audio from this YouTube channel", "download from my
  favourite channels", "add channel to favourites", "transcribe YouTube video",
  or any YouTube channel/video audio retrieval or transcription request.
version: 1.3.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - pip
---

# YouTube Skill

Use this skill for YouTube-related tasks. Supports audio downloading, transcription, metadata saving, and favourite channel management.

## Stored data

For each processed video, three files are saved (all keyed by YouTube video ID):

| File | Default location | Contents |
|------|-----------------|----------|
| `<video_id>.m4a` | `./audio/` | Audio in native M4A format |
| `<video_id>.txt` | `./transcripts/` | Plain-text transcript, one segment per line |
| `<video_id>.json` | `./metadata/` | Video metadata (see fields below) |

**Metadata JSON fields** — you can read these files any time you need context about a video:

| Field | Description |
|-------|-------------|
| `id` | YouTube video ID |
| `title` | Video title |
| `description` | Full video description |
| `channel` | Channel display name |
| `channel_id` | Stable channel ID (e.g. `UCxxxxxx`) |
| `channel_url` | Channel URL |
| `uploader` | Uploader name (usually same as channel) |
| `uploader_id` | Uploader handle (e.g. `@mkbhd`) |
| `upload_date` | Upload date as `YYYYMMDD` string |
| `duration` | Duration in seconds |
| `view_count` | View count at time of download |
| `like_count` | Like count at time of download |
| `comment_count` | Comment count at time of download |
| `tags` | List of tags |
| `categories` | List of YouTube categories |
| `webpage_url` | Full video URL |
| `thumbnail` | Thumbnail URL |

These files are plain JSON — read them directly whenever you need to look up a video's title, channel, description, upload date, or any other field listed above.

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
| `--transcripts DIR` | `-t` | Directory to save transcripts | `./transcripts` |
| `--metadata DIR` | `-m` | Directory to save metadata JSON files | `./metadata` |

At least one of `--channel` or `--from-favourites` is required. Both can be combined.

### Accepted channel URL formats

- `https://www.youtube.com/@Handle`
- `https://www.youtube.com/channel/UCxxxxxxxxx`
- `https://www.youtube.com/c/ChannelName`

### Output format

Each video prints up to three lines — one each for metadata, audio, and transcription:

```
METADATA_SAVED <video_id>        # metadata JSON was fetched and saved
DOWNLOADED <video_id>            # audio was fetched and saved
TRANSCRIBED <video_id>           # transcript was created

METADATA_SKIPPED <video_id>      # metadata file already exists
SKIPPED <video_id>               # audio already exists
TRANSCRIPT_SKIPPED <video_id>    # transcript already exists

METADATA_ERROR <video_id> <msg>  # metadata fetch failed
ERROR <video_id> <msg>           # audio download failed
TRANSCRIPT_ERROR <video_id> <msg># transcription failed
```

Exit code is `0` on full success, `1` if any step failed.

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

- All three outputs (metadata, audio, transcript) are keyed by video ID — each is skipped independently if the file already exists
- No ffmpeg required — audio is downloaded in native M4A format from YouTube
- If a channel has fewer than `--n` videos, all available videos are downloaded

---

## Feature: Transcribe Audio

Transcribe already-downloaded audio files using `faster-whisper` (base model, language auto-detected).
Transcripts are saved as `<video_id>.txt`, one segment per line.

### Script

```
python3 <skill_dir>/scripts/transcribe.py [options]
```

### Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--audio-dir DIR` | `-a` | Directory containing audio files | `./audio` |
| `--transcripts-dir DIR` | `-t` | Directory to save transcripts | `./transcripts` |
| `--video-id ID` | `-v` | Transcribe a specific video ID only | all files |

### Output format

```
TRANSCRIBED <video_id>           # transcript was created
TRANSCRIPT_SKIPPED <video_id>    # transcript already exists
TRANSCRIPT_ERROR <video_id> <msg># transcription failed
```

### Examples

Transcribe all audio files that don't have a transcript yet:
```
python3 <skill_dir>/scripts/transcribe.py
```

Transcribe a specific video:
```
python3 <skill_dir>/scripts/transcribe.py --video-id dQw4w9WgXcQ
```

Transcribe from a custom audio directory:
```
python3 <skill_dir>/scripts/transcribe.py --audio-dir ~/music/youtube --transcripts-dir ~/music/transcripts
```
