#!/usr/bin/env python3
"""Rotating ASCII Prouvé Standard chair. Ctrl-C to stop."""
import json, time, sys, os

frames = json.load(open(os.path.join(os.path.dirname(__file__), 'chair_frames.json')))
try:
    sys.stdout.write('\x1b[?25l')  # hide cursor
    while True:
        for f in frames:
            sys.stdout.write('\x1b[H\x1b[2J' + f + '\n')
            sys.stdout.flush()
            time.sleep(0.11)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write('\x1b[?25h\n')
