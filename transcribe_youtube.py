#!/usr/bin/env python3
import re
import os
from datetime import datetime
from typing import Optional

import click
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url_or_id: str) -> Optional[str]:
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([^#&?]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        m = re.search(pattern, url_or_id)
        if m:
            return m.group(1)
    return None


def fetch_transcript(video_id: str) -> str:
    api = YouTubeTranscriptApi()
    preferred_languages = ["ja", "ja-JP", "en", "en-US"]
    last_error: Optional[Exception] = None
    for lang in preferred_languages:
        try:
            chunks = api.fetch(video_id, languages=[lang])
            return " ".join([c.text for c in chunks])
        except Exception as e:  # noqa: BLE001
            last_error = e
            continue
    try:
        chunks = api.fetch(video_id)
        return " ".join([c.text for c in chunks])
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Could not fetch transcript: {e or last_error}")


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def format_output(text: str, url: str, fmt: str) -> str:
    if fmt == "txt":
        return text
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"# YouTube Transcript\n\n"
        f"**URL:** {url}\n\n"
        f"**Generated:** {ts}\n\n"
        f"---\n\n{text}\n"
    )


@click.command()
@click.argument("url")
@click.option("--output", "output_path", default="output/transcript.md", help="Output file path")
@click.option("--format", "fmt", type=click.Choice(["md", "txt"]), default="md", help="Output format")
def main(url: str, output_path: str, fmt: str) -> None:
    video_id = extract_video_id(url)
    if not video_id:
        raise click.ClickException("Invalid YouTube URL or ID")

    text = fetch_transcript(video_id)
    ensure_parent_dir(output_path)
    body = format_output(text, url, fmt)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(body)
    click.echo(f"Saved transcript to {output_path}")


if __name__ == "__main__":
    main()


