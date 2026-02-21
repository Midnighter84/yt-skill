#!/usr/bin/env python3
import argparse
import os
import sys

import yt_dlp


AUDIO_EXTENSIONS = ["m4a", "webm", "opus", "ogg", "mp3"]


def find_existing(video_id, output_dir):
    for ext in AUDIO_EXTENSIONS:
        path = os.path.join(output_dir, f"{video_id}.{ext}")
        if os.path.exists(path):
            return path
    return None


def get_channel_videos(channel_url, n):
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "playlist_items": f"1-{n}",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
    if "entries" in info:
        return [(e["id"], e.get("title", e["id"])) for e in info["entries"] if e]
    return [(info["id"], info.get("title", info["id"]))]


def download_audio(video_id, output_dir):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    parser = argparse.ArgumentParser(
        description="Download audio from YouTube channels."
    )
    parser.add_argument(
        "--channel", "-c",
        action="append",
        required=True,
        metavar="URL",
        help="YouTube channel URL (repeat for multiple channels)",
    )
    parser.add_argument(
        "--n", "-n",
        type=int,
        default=5,
        metavar="COUNT",
        help="Number of latest videos per channel (default: 5)",
    )
    parser.add_argument(
        "--output", "-o",
        default="./audio",
        metavar="DIR",
        help="Output directory (default: ./audio)",
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    exit_code = 0

    for channel_url in args.channel:
        try:
            videos = get_channel_videos(channel_url, args.n)
        except Exception as e:
            print(f"ERROR channel:{channel_url} {e}", flush=True)
            exit_code = 1
            continue

        for video_id, _title in videos:
            try:
                if find_existing(video_id, args.output):
                    print(f"SKIPPED {video_id}", flush=True)
                else:
                    download_audio(video_id, args.output)
                    print(f"DOWNLOADED {video_id}", flush=True)
            except Exception as e:
                print(f"ERROR {video_id} {e}", flush=True)
                exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
