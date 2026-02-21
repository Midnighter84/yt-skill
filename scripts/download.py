#!/usr/bin/env python3
import argparse
import os
import sys

import yt_dlp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcribe import load_model, transcribe_audio

DEFAULT_FAVOURITES_FILE = os.path.expanduser("~/.yt-skill/favourites.txt")


def load_favourites(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


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
        default=[],
        metavar="URL",
        help="YouTube channel URL (repeat for multiple channels)",
    )
    parser.add_argument(
        "--from-favourites", "-F",
        action="store_true",
        help="Download from all channels in the favourites file",
    )
    parser.add_argument(
        "--favourites-file",
        default=DEFAULT_FAVOURITES_FILE,
        metavar="PATH",
        help=f"Favourites file path (default: {DEFAULT_FAVOURITES_FILE})",
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
        help="Output directory for audio files (default: ./audio)",
    )
    parser.add_argument(
        "--transcripts", "-t",
        default="./transcripts",
        metavar="DIR",
        help="Output directory for transcripts (default: ./transcripts)",
    )
    args = parser.parse_args()

    channels = list(args.channel)
    if args.from_favourites:
        fav_channels = load_favourites(args.favourites_file)
        if not fav_channels:
            print(f"ERROR no favourite channels found in {args.favourites_file}", flush=True)
            sys.exit(1)
        channels.extend(fav_channels)

    if not channels:
        parser.error("at least one --channel URL or --from-favourites is required")

    os.makedirs(args.output, exist_ok=True)
    os.makedirs(args.transcripts, exist_ok=True)

    exit_code = 0
    model = None  # lazy-loaded on first transcription

    for channel_url in channels:
        try:
            videos = get_channel_videos(channel_url, args.n)
        except Exception as e:
            print(f"ERROR channel:{channel_url} {e}", flush=True)
            exit_code = 1
            continue

        for video_id, _title in videos:
            # --- audio ---
            try:
                audio_path = find_existing(video_id, args.output)
                if audio_path:
                    print(f"SKIPPED {video_id}", flush=True)
                else:
                    download_audio(video_id, args.output)
                    print(f"DOWNLOADED {video_id}", flush=True)
                    audio_path = find_existing(video_id, args.output)
            except Exception as e:
                print(f"ERROR {video_id} {e}", flush=True)
                exit_code = 1
                continue

            # --- transcription ---
            transcript_path = os.path.join(args.transcripts, f"{video_id}.txt")
            if os.path.exists(transcript_path):
                print(f"TRANSCRIPT_SKIPPED {video_id}", flush=True)
            elif audio_path is None:
                print(f"TRANSCRIPT_ERROR {video_id} audio file not found", flush=True)
                exit_code = 1
            else:
                try:
                    if model is None:
                        model = load_model()
                    transcribe_audio(model, audio_path, transcript_path)
                    print(f"TRANSCRIBED {video_id}", flush=True)
                except Exception as e:
                    print(f"TRANSCRIPT_ERROR {video_id} {e}", flush=True)
                    exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
