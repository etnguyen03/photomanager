"""
Reads the file passed as the only command line argument.

This script chroots into the parent directory to prevent
symlinks from reading other files on disk.

The contents are base64-ed and are printed to
stdout as a JSON dump along with
their MIME types, like this:

{"hello.txt": {"data": "[base64 of file contents]", "mime": "text/plain"}}
"""

import argparse
import base64
import json
import os
from pathlib import Path

import magic

argparser = argparse.ArgumentParser()
argparser.add_argument("file", help="File to read", type=Path)
args = argparser.parse_args()

assert os.path.isfile(args.file), "This file does not exist"
assert (
    os.geteuid() == 0
), "This script must be ran as root"  # chroot can only be done as root

# This must be created before chrooting
m = magic.Magic(mime=True)

# Chroot into this directory
os.chdir(args.file.parent)
os.chroot(args.file.parent)

# Get the content of the file
with open(args.file.name, "rb") as file:
    contents = file.read()

print(
    json.dumps(
        {
            str(args.file): {
                "data": base64.b64encode(contents).decode(),
                "mime": m.from_file(str(args.file.name)),
                "size": os.path.getsize(args.file.name),
            }
        }
    )
)
