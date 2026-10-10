#!/usr/bin/env python3
r"""
score_beautifier.py - Post-processor for LilyPond scores in Bach in the Mirror
Written for Bach in the Mirror (pianomirror.org)

Cleans and beautifies intermediate LilyPond (.ly) files generated during transpilation:
- Strips erratic, measure-by-measure \ottava churn (e.g. flickering \ottava #0 / \ottava #-1).
- Eliminates redundant stacked ottava commands.
- Ensures proper octave placement (\transpose c c') for inverted voices.
- Normalizes whitespace and score layout for clean, publication-ready engraving.
"""

import sys
import os
import re


def beautify_lilypond_content(content: str, mode: int = None) -> str:
    """
    Cleans and optimizes LilyPond score content.
    """
    lines = content.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        # Remove all erratic line-by-line ottava commands
        if stripped.startswith(r"\ottava"):
            continue
        cleaned_lines.append(line)

    result = "\n".join(cleaned_lines)

    # Clean up multiple consecutive blank lines
    result = re.sub(r"\n{3,}", "\n\n", result)

    # If mode is provided and \transpose c c' is not already present, ensure octave wrappers
    if mode is not None and "\\transpose c c'" not in result:
        if mode == 1:
            # Voice 2 is inverted: should be shifted up 1 octave if not already wrapped
            if "voicetwo = {" in result:
                result = result.replace("voicetwo = {", "voicetwo = \\transpose c c' {", 1)
        elif mode == 2:
            # Voice 1 is inverted: should be shifted up 1 octave if not already wrapped
            if "voiceone = {" in result:
                result = result.replace("voiceone = {", "voiceone = \\transpose c c' {", 1)
        elif mode == 3:
            # Both voices are inverted: both should be shifted up 1 octave
            if "voiceone = {" in result:
                result = result.replace("voiceone = {", "voiceone = \\transpose c c' {", 1)
            if "voicetwo = {" in result:
                result = result.replace("voicetwo = {", "voicetwo = \\transpose c c' {", 1)

    return result.strip() + "\n"


def beautify_lilypond_file(file_path: str, mode: int = None) -> None:
    """
    Reads a LilyPond file, beautifies its content, and overwrites the file in place.
    If mode is None, attempts to detect mode from filename or markup in the file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Detect mode if not explicitly passed
    if mode is None:
        basename = os.path.basename(file_path)
        m = re.match(r"^([0-3])_", basename)
        if m:
            mode = int(m.group(1))
        elif "Left Hand Ascending" in content:
            mode = 1
        elif "Right Hand Descending" in content:
            mode = 2
        elif "Mirror Image" in content:
            mode = 3
        elif "No Mirroring" in content:
            mode = 0

    beautified = beautify_lilypond_content(content, mode=mode)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(beautified)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 score_beautifier.py <file.ly> [mode: 0-3]")
        sys.exit(1)

    target_file = sys.argv[1]
    mode = int(sys.argv[2]) if len(sys.argv) > 2 else None

    beautify_lilypond_file(target_file, mode=mode)
    print(f"Beautified: {target_file}")


if __name__ == "__main__":
    main()
