#!/usr/bin/env python3
import argparse
import os
import sys

DEFAULT_FAVOURITES_FILE = os.path.expanduser("~/.yt-skill/favourites.txt")


def load_favourites(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def save_favourites(path, channels):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for channel in channels:
            f.write(channel + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Manage favourite YouTube channels."
    )
    parser.add_argument(
        "--file", "-f",
        default=DEFAULT_FAVOURITES_FILE,
        metavar="PATH",
        help=f"Favourites file path (default: {DEFAULT_FAVOURITES_FILE})",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--add", "-a",
        metavar="URL",
        help="Add a YouTube channel URL to favourites",
    )
    group.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all favourite channels",
    )
    group.add_argument(
        "--remove", "-r",
        metavar="URL",
        help="Remove a YouTube channel URL from favourites",
    )

    args = parser.parse_args()

    channels = load_favourites(args.file)

    if args.add:
        url = args.add.strip()
        if url in channels:
            print(f"ALREADY_EXISTS {url}", flush=True)
        else:
            channels.append(url)
            save_favourites(args.file, channels)
            print(f"ADDED {url}", flush=True)

    elif args.list:
        if not channels:
            print("(no favourite channels saved)", flush=True)
        else:
            for channel in channels:
                print(channel, flush=True)

    elif args.remove:
        url = args.remove.strip()
        if url not in channels:
            print(f"NOT_FOUND {url}", flush=True)
            sys.exit(1)
        channels.remove(url)
        save_favourites(args.file, channels)
        print(f"REMOVED {url}", flush=True)


if __name__ == "__main__":
    main()
