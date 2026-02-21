#!/usr/bin/env python3
import argparse
import os
import sys

from faster_whisper import WhisperModel

AUDIO_EXTENSIONS = ["m4a", "webm", "opus", "ogg", "mp3"]


def load_model():
    return WhisperModel("base", device="cpu", compute_type="int8")


def find_audio(video_id, audio_dir):
    for ext in AUDIO_EXTENSIONS:
        path = os.path.join(audio_dir, f"{video_id}.{ext}")
        if os.path.exists(path):
            return path
    return None


def transcribe_audio(model, audio_path, out_path):
    segments, _ = model.transcribe(audio_path, language=None)
    with open(out_path, "w") as f:
        for segment in segments:
            f.write(segment.text.strip() + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe downloaded YouTube audio using faster-whisper."
    )
    parser.add_argument(
        "--audio-dir", "-a",
        default="./audio",
        metavar="DIR",
        help="Directory containing audio files (default: ./audio)",
    )
    parser.add_argument(
        "--transcripts-dir", "-t",
        default="./transcripts",
        metavar="DIR",
        help="Directory to save transcripts (default: ./transcripts)",
    )
    parser.add_argument(
        "--video-id", "-v",
        metavar="ID",
        help="Transcribe a specific video ID only (default: all audio files)",
    )
    args = parser.parse_args()

    os.makedirs(args.transcripts_dir, exist_ok=True)

    if args.video_id:
        video_ids = [args.video_id]
    else:
        video_ids = []
        for fname in sorted(os.listdir(args.audio_dir)):
            for ext in AUDIO_EXTENSIONS:
                if fname.endswith(f".{ext}"):
                    video_ids.append(fname[: -len(ext) - 1])
                    break

    to_transcribe = []
    for vid in video_ids:
        tp = os.path.join(args.transcripts_dir, f"{vid}.txt")
        if os.path.exists(tp):
            print(f"TRANSCRIPT_SKIPPED {vid}", flush=True)
        else:
            audio = find_audio(vid, args.audio_dir)
            if audio:
                to_transcribe.append((vid, audio, tp))
            else:
                print(f"TRANSCRIPT_ERROR {vid} audio file not found", flush=True)

    if not to_transcribe:
        return

    exit_code = 0
    model = load_model()
    for vid, audio, tp in to_transcribe:
        try:
            transcribe_audio(model, audio, tp)
            print(f"TRANSCRIBED {vid}", flush=True)
        except Exception as e:
            print(f"TRANSCRIPT_ERROR {vid} {e}", flush=True)
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
