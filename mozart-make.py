#!/usr/bin/python3

# mozart-make.py - Drive program for mozart-compiler, specifically to create bach-in-the-mirror
# Written by: Benjamin Pritchard / Kundalini Software
# www.kundalinisoftware.com

"""
mozart-make.py

Hacked-together driver program for mozart-compile. The idea is to call mozart-compile and lilypond
to generate all the Bach inventions.

Benjamin Pritchard / Kundalini Software

Version History:
27-June-2020    Version 1.0     Initial release
26-Sept-2021    Version 1.1     Cleanup; Updated to work under Linux

"""

import os
import subprocess
import shlex
from os import path

Version_String = "1.1"

input_file_path = "mozart-transpose-input/"
output_file_path = "mozart-transpose-output/"
png_file_path = output_file_path + "png/"
tmp_file_path = output_file_path + "tmp/"

inputfiles = ["01", "02", "03", "04", "05", "06", "07",
              "08", "09", "10", "11", "12", "13", "14", "15"]

inputfiles = ["01"]


def wrap_in_quotes(input_str):
    return '"' + input_str + '"'


print("Mozart Make, version " + Version_String)
print("Written by Benjamin Pritchard / Kundalini Software")

# if output_file_path does not exist, return true
# if time_stamp of files don't match, return true
# otherwise, return false


def shouldProcessFile(input_file, output_file):
    return True


# just make sure our output directory exists; we will leave all the .png files here...
if not os.path.exists(output_file_path):
    os.mkdir(output_file_path)

# just make sure our output directory exists; we will leave all the .png files here...
if not os.path.exists(png_file_path):
    os.mkdir(png_file_path)

# and then make a .tmp directory to hold the intermediate files. we will delete it when we are done...
if not os.path.exists(tmp_file_path):
    os.mkdir(tmp_file_path)
else:
    path, dirs, files = next(os.walk(tmp_file_path))
    file_count = len(files)
    if file_count > 0:
        print("Warning: directory " + tmp_file_path +
              " already exists and is not empty; cannot continue. Please make sure it is empty before running this program.")
        exit()

for f in inputfiles:
    input_file = input_file_path + f + ".ly"

    # create one file for each key
    for transpose in range(0, 1):
        split = 56

        # and each mode
        for mode in range(0, 1):

            mozart_compile_output_file = output_file_path + "tmp/" + \
                str(mode) + "_" + f + "_" + str(transpose) + ".ly"

            lilypond_output_file = png_file_path + \
                str(mode) + "_" + f + "_" + str(transpose)

            if not shouldProcessFile(input_file, lilypond_output_file):
                print("skipping file " + input_file + " because " +
                      lilypond_output_file + " is already up to date.")
                break

            # ---------------------------------------------------------------------------------------------------
            # execute mozart-compile
            # ---------------------------------------------------------------------------------------------------

            full_command = 'python3 mozart-compile.py --transpose=' + str(transpose) + ' --split=' + str(split) + ' --mode=' + str(
                mode) + ' ' + wrap_in_quotes(input_file) + ' ' + wrap_in_quotes(mozart_compile_output_file)

            if os.system(full_command) != 0:
                exit()

            # ---------------------------------------------------------------------------------------------------
            # execute lilypond
            # ---------------------------------------------------------------------------------------------------

            full_command = 'lilypond --png -o ' + \
                wrap_in_quotes(lilypond_output_file) + ' ' + \
                wrap_in_quotes(mozart_compile_output_file)

            if os.system(full_command) != 0:
                exit()

            # ---------------------------------------------------------------------------------------------------
            # we want to set the modified time of the .png file to the same as the original .ly file.
            # however, we only need to do it for the first page, because we will be able to
            # tell if the .png files are to date by comparing just the first page against
            # the modified time of the .ly file
            # ---------------------------------------------------------------------------------------------------

            stinfo = os.stat(input_file)
            os.utime(lilypond_output_file + "-page1.png",
                     (stinfo.st_atime, stinfo.st_mtime))

            # ---------------------------------------------------------------------------------------------------
            # just clean up the tmp file (created by mozart-compile)
            # ---------------------------------------------------------------------------------------------------
            os.remove(mozart_compile_output_file)

# ---------------------------------------------------------------------------------------------------
# totally clean up after ourselves by completely deleting the tmp directory
# ---------------------------------------------------------------------------------------------------
os.rmdir(tmp_file_path)

# finished!
print("Mozart-Make completed successfully")
