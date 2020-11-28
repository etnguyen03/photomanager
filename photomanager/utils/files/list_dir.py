"""
Recursively lists the contents of the directory passed as
the only command line argument. This script chroots into
that directory, then lists, to help mitigate security
vulnerabilities (for instance, if a file is a cleverly
designed symlink).

The contents are printed to stdout as a JSON dump with
their MIME types as determined by python-magic, like this:

{"hello.jpeg": "image/jpeg", "hello/hello.txt": "text/plain"}
"""

import argparse
import json
import os

import magic

argparser = argparse.ArgumentParser()
argparser.add_argument("directory", help="Directory to list/traverse", type=str)
args = argparser.parse_args()

assert os.path.isdir(args.directory), "This directory does not exist"

# This must be created before chrooting
m = magic.Magic(mime=True)

# Chroot into this directory
os.chroot(args.directory)

# List the files in this directory
# https://stackoverflow.com/questions/19309667/recursive-os-listdir
files = [os.path.join(dp, f) for dp, dn, fn in os.walk("/") for f in fn]

# Get the MIME types of each file in this directory
files_mime_dict = {}

for file in files:
    if os.path.exists(file):
        files_mime_dict[file] = m.from_file(file)

print(json.dumps(files_mime_dict))
