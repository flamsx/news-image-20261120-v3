#!/usr/bin/env python3
"""Entry point for the news-image-20261120 v3 front page.

The page itself was pre-rendered by draw.py (Pillow + the Lexend font in
fonts/) into entry.png, which ships in this repository.  This program
only copies those bytes to the output directory, so it runs in the
sandbox with the standard library alone and writes identical bytes on
every run.
"""
import hashlib
import os


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    with open(src, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG file")
    if len(data) > 1048576:
        raise SystemExit("entry.png exceeds 1 MiB")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as f:
        f.write(data)
    print("wrote %s: %d bytes sha256 %s"
          % (dst, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
