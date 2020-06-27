"""
mozart-make.py

Hacked-together driver program for mozart-compile. The idea is to call mozart compile and lilypond
to generate all the Bach inventions.
    
Benjamin Pritchard / Kundalini Software

Version History:
27-June-2020    Verison 1.0     Initial release

"""

import os
import subprocess, shlex
from os import path

Version_String = "1.0"

def wrap_in_quotes(input_str):
    return '"' + input_str + '"'

print("Mozart Make, version " + Version_String)
print("Written by Benjamin Pritchard / Kundalini Software")

input_file_path     = "C:\\kundalini\\bach inventions\\mozart-transpose-input\\"
output_file_path    = "C:\\kundalini\\bach inventions\\mozart-transpose-output\\tmp\\"
edited_file_path    = "C:\kundalini\\bach inventions\\mozart-transpose-output\\hand_edited\\"
diff_path           = "C:\\kundalini\\bach inventions\\mozart-transpose-output\\diffs\\"

orig_output_file_path = output_file_path

diff_command    = "C:\\Program Files\\Git\\usr\\bin\\diff.exe"
patch_command   = "C:\\Program Files\\Git\\usr\\bin\\patch.exe"

Create_Scores   = True
Create_Diff     = False
Apply_Patch     = False

inputfiles = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15"]

for f in inputfiles:
    input_file = input_file_path + f + ".ly"

    # make a new directory to work in...
    output_file_path = orig_output_file_path + f + "\\"
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path, True)

    # create one file for each key
    for transpose in range(11, 12):
        split = 56

        for mode in range(0, 4):
            mozart_compile_output_file = output_file_path + str(mode) + "_" + f + "_" + str(transpose) + ".ly"
            lilypond_output_file = output_file_path + str(mode) + "_" + f + "_" + str(transpose) 

            if (Create_Scores):
                full_command = 'python mozart-compile.py /transpose=' + str(transpose) + ' /split=' + str(split) + ' /mode=' + str(mode) + ' ' + wrap_in_quotes(input_file) + ' ' + wrap_in_quotes(mozart_compile_output_file)
                if os.system(full_command) != 0:
                    exit()

                full_command = 'lilypond --png -o ' + wrap_in_quotes(lilypond_output_file) + ' ' + wrap_in_quotes(mozart_compile_output_file)
                if os.system(full_command) != 0:
                    exit()


            if (Create_Diff):
                edited_version = edited_file_path + '\\' + f + "\\" + str(mode) + "_" + f + "_" + str(transpose) + ".ly"
                full_command = wrap_in_quotes(diff_command) + ' ' + wrap_in_quotes(lilypond_output_file + '.ly') + ' ' + wrap_in_quotes(edited_version) 
            
                print(full_command)

                result = subprocess.run(shlex.split(full_command), stdout=subprocess.PIPE, universal_newlines=True)

                diff_output = diff_path + str(mode) + "_" + f + "_" + str(transpose) + ".patch"

                if (result.stdout != ""):
                    with open(diff_output, "w+") as fp:
                        fp.write(result.stdout)

            if (Apply_Patch):
                edited_version = edited_file_path + '\\' + f + "\\" + str(mode) + "_" + f + "_" + str(transpose) + ".ly"
                diff_output = diff_path + str(mode) + "_" + f + "_" + str(transpose) + ".patch"
                full_command = wrap_in_quotes(patch_command) + ' ' + wrap_in_quotes(lilypond_output_file + '.ly') + ' ' + wrap_in_quotes(diff_output)
            
                if path.exists(diff_output):
                    print(full_command)
                    result = subprocess.run(shlex.split(full_command), stdout=subprocess.PIPE, universal_newlines=True)

                    if (result.stdout != ""):
                        with open(diff_output, "w+") as fp:
                            fp.write(result.stdout)