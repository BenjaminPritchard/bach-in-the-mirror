#!/usr/bin/env python3

# mozart-make.py - Parallel driver program for mozart-compile, specifically to create bach-in-the-mirror
# Written by: Benjamin Pritchard / Kundalini Software
# www.kundalinisoftware.com

"""
mozart-make.py

Parallel build driver for mozart-compile. Transpiles Bach Two-Part Inventions
across keys and modes using multi-worker parallelism (similar to `make -jN`)
and compiles them to PNG scores via LilyPond.

Benjamin Pritchard / Kundalini Software

Version History:
27-June-2020    Version 1.0     Initial release
26-Sept-2021    Version 1.1     Cleanup; Updated to work under Linux
20-Sept-2026    Version 2.0     Upgraded to parallel execution engine (-j / --jobs)
"""

import os
import sys
import subprocess
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

Version_String = "2.0"

input_file_path = "mozart-transpose-input/"
output_file_path = "mozart-transpose-output/"
png_file_path = os.path.join(output_file_path, "png/")
tmp_file_path = os.path.join(output_file_path, "tmp/")

ALL_INVENTIONS = [
    "01", "02", "03", "04", "05", "06", "07",
    "08", "09", "10", "11", "12", "13", "14", "15"
]


def shouldProcessFile(input_file, output_file):
    """
    Returns True if output_file does not exist or if input_file is newer than output_file.
    """
    if not os.path.exists(output_file):
        return True

    stinfo1 = os.stat(input_file)
    stinfo2 = os.stat(output_file)

    if stinfo1.st_mtime > stinfo2.st_mtime:
        return True

    return False


def process_task(task):
    """
    Worker task: Transpiles one invention in one key/mode and renders it via LilyPond.
    Returns (task, status, message) where status is 'OK', 'SKIPPED', or 'ERROR'.
    """
    f, transpose, split, mode, force = task
    input_file = os.path.join(input_file_path, f + ".ly")
    mozart_compile_output_file = os.path.join(
        tmp_file_path, f"{mode}_{f}_{transpose}.ly"
    )
    lilypond_output_file = os.path.join(
        png_file_path, f"{mode}_{f}_{transpose}"
    )
    expected_png = lilypond_output_file + "-page1.png"

    # Check if target is already up-to-date
    if not force and not shouldProcessFile(input_file, expected_png):
        return (task, "SKIPPED", f"Invention {f} (mode={mode}, transpose={transpose}) is up to date.")

    # 1. Execute mozart-compile
    compile_cmd = [
        sys.executable,
        "mozart-compile.py",
        f"--transpose={transpose}",
        f"--split={split}",
        f"--mode={mode}",
        input_file,
        mozart_compile_output_file
    ]

    res = subprocess.run(compile_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        err_msg = res.stderr.strip() or res.stdout.strip()
        return (task, "ERROR", f"mozart-compile failed for {f} (mode={mode}, transpose={transpose}):\n{err_msg}")

    # 2. Execute lilypond
    lilypond_cmd = [
        "lilypond",
        "--png",
        "-o",
        lilypond_output_file,
        mozart_compile_output_file
    ]

    res = subprocess.run(lilypond_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        err_msg = res.stderr.strip() or res.stdout.strip()
        return (task, "ERROR", f"lilypond failed for {f} (mode={mode}, transpose={transpose}):\n{err_msg}")

    return (task, "OK", f"Invention {f} (mode={mode}, transpose={transpose}) generated successfully.")


def main():
    parser = argparse.ArgumentParser(
        description=f"Mozart Make v{Version_String} - Parallel score transpiler and renderer."
    )
    detected_cpus = os.cpu_count() or 4
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=detected_cpus,
        help=f"Number of parallel worker jobs (default: auto-detected CPU count: {detected_cpus})"
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Build all 15 Bach Two-Part Inventions"
    )
    parser.add_argument(
        "-c", "--clean",
        action="store_true",
        help="Clean the temporary output directory before building"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force rebuilding scores even if already up to date"
    )
    parser.add_argument(
        "-m", "--modes",
        nargs="+",
        type=int,
        default=[0, 1, 2, 3],
        help="Mirroring modes to generate: 0=No Mirroring, 1=Left Hand Ascending, 2=Right Hand Descending, 3=Mirror Image (default: [0, 1, 2, 3])"
    )
    parser.add_argument(
        "files",
        nargs="*",
        default=[],
        help="Specific invention numbers to build (e.g. 01 02 03). Defaults to all 15 inventions if none specified."
    )

    args = parser.parse_args()

    # Determine worker count dynamically
    jobs = args.jobs if (args.jobs and args.jobs > 0) else detected_cpus

    print(f"Mozart Make, version {Version_String}")
    print("Written by Benjamin Pritchard / Kundalini Software")
    print(f"Parallel Worker Threads: {jobs}")

    # Ensure required directories exist
    os.makedirs(output_file_path, exist_ok=True)
    os.makedirs(png_file_path, exist_ok=True)
    os.makedirs(tmp_file_path, exist_ok=True)

    if args.clean:
        print(f"Cleaning temporary directory: {tmp_file_path}")
        for item in os.listdir(tmp_file_path):
            item_path = os.path.join(tmp_file_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)

    # Determine which inventions to build
    selected_files = []
    if args.files:
        for f in args.files:
            # Normalize to 2-digit format (e.g., '1' -> '01')
            normalized = f.strip().zfill(2)
            if normalized in ALL_INVENTIONS:
                selected_files.append(normalized)
            else:
                print(f"Warning: Unknown invention '{f}', skipping.")
    elif args.all or not args.files:
        # Default to all 15 inventions
        selected_files = ALL_INVENTIONS

    if not selected_files:
        print("No valid inventions selected for build.")
        sys.exit(1)

    # Build task matrix
    tasks = []
    for f in selected_files:
        for transpose in range(0, 12):
            split = 56
            for mode in args.modes:
                tasks.append((f, transpose, split, mode, args.force))

    total = len(tasks)
    print(f"Queueing {total} task(s) for inventions: {', '.join(selected_files)}")
    print(f"Executing tasks with -j{jobs} concurrency...\n")

    start_time = time.time()
    completed_count = 0
    skipped_count = 0
    error_count = 0

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        future_to_task = {executor.submit(process_task, t): t for t in tasks}
        for future in as_completed(future_to_task):
            task, status, msg = future.result()
            f, transpose, split, mode, _ = task
            completed_count += 1
            pct = (completed_count / total) * 100

            if status == "OK":
                print(f"[{completed_count:3d}/{total:3d}] ({pct:5.1f}%) [OK]      Invention {f} (transpose={transpose:2d}, mode={mode})")
            elif status == "SKIPPED":
                skipped_count += 1
                print(f"[{completed_count:3d}/{total:3d}] ({pct:5.1f}%) [SKIPPED] Invention {f} (transpose={transpose:2d}, mode={mode})")
            else:
                error_count += 1
                print(f"[{completed_count:3d}/{total:3d}] ({pct:5.1f}%) [ERROR]   Invention {f} (transpose={transpose:2d}, mode={mode}): {msg}")

    elapsed = time.time() - start_time
    generated_count = total - skipped_count - error_count

    print("-" * 60)
    print(f"Mozart-Make completed in {elapsed:.2f} seconds.")
    print(f"  Total tasks:  {total}")
    print(f"  Generated:    {generated_count}")
    print(f"  Skipped:      {skipped_count}")
    print(f"  Errors:       {error_count}")
    print("-" * 60)

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
