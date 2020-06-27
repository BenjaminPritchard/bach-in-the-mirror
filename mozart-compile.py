"""

Example usage of the Mozart-Tranposition-Engine used here to produce symmetrically inverted versions
of all 15 Bach 2 Part inventions.

mozart-compile.py
    - please see the Lilypond Scores in mozart-compile-input for example input files; they are 
    slightly and are not exactly in lilypond format!!

command line:
    mozart-compile /transpose=X /split=X /mode=X input_file output_file  
    modes:
        0 no mirroring
        l Left Hand Ascending
        2 Right Hand Ascending
        3 Mirror
        4 Left Hand Ascending Call Response
        5 Right Hand Ascending Call Response

    All command line parameters are required

Example:
    mozart-compile /transpose=X /split=X /mode=X input_file output_file
    
Benjamin Pritchard / Kundalini Software

Version History:
27-June-2020    Verison 1.0     Initial release

"""

from tempfile import mkstemp
import os
import sys
import ly.cli.main          # we don't really use this, but it is a convienent way to make sure it is available

Version_String = "1.0"

# this has to correspond to the location of the ly command from the package python-ly
# this will need to be updated before this script will work!!
# https://github.com/frescobaldi/python-ly
ly_command = "c:\\srcExamples\\python-ly-0.9.5\\bin\\ly"

debug_mode = False

class Note:

    # Initializer / Instance Attributes
    def __init__(self, token, is_note, absolute_num):
        self.token = token
        self.is_note = is_note
        self.absolute_num = absolute_num

# looks through list of tokens, and if it finds Ch in a token, strip it out, and add the character as a stand-alone entry in the list
# example:
#   tokenize(['(1','2','3', '4)'], '[') would yield: ['(', '1', '2', '3', '4)']
def stand_alone_token(tokens, Ch):
    retval = []
    for token in tokens:
        if (token.find(Ch) > 0):
            retval.append(token.replace(Ch,""))
            retval.append(Ch)
        else:
            retval.append(token)
    return retval

def leftMatch(input, search_string):
    return (input.find(search_string) == 0)

def InRange(x, min, max):
    return (x >= min) and (x <= max)

# takes an input string, with
def tokenize(input):

    # first strip off anything to the right of the %
    # (but we remember what was over there so we can put it back on later)
    comment_position = input.find("%")
    if (comment_position >= 0):
        comment = input[comment_position:]
        input = input[0:comment_position]
    else:
        comment=""    

    # it helps our parsing logic if brackets have spaces around these
    input = input.replace("["," [ ")
    input = input.replace("]"," ] ")

    # it helps our parsing logic if brackets have spaces around these
    input = input.replace("<"," < ")
    input = input.replace(">"," > ")

     # it helps our parsing logic if brackets have spaces around these
    input = input.replace("("," ( ")
    input = input.replace(")"," ) ")

    input = input.replace("^"," ^ ")
    input = input.replace("\\", " \\")            # note: no space after the slash...
 
    # split the input string into pieces, deliminated by spaces
    tokens = input.split()

    # make each of the following characters an individual token)
    tokens = stand_alone_token(tokens, "[")
    tokens = stand_alone_token(tokens, "]")
    tokens = stand_alone_token(tokens, "<")
    tokens = stand_alone_token(tokens, ">")
    tokens = stand_alone_token(tokens, "(")
    tokens = stand_alone_token(tokens, ")")

    # similar to the above, but strip off trailing number (which can include a period) and make
    # it into a token
    #   <put example here>
    token2 = []
    for token in tokens:
        tmp = ""
        if (token[-1] in  ['0','1','2','3','4','5','6','7','8','9','.','-']):
            while token[-1] in ['0','1','2','3','4','5','6','7','8','9','.' ,'-']:
                tmp = token[-1] + tmp  
                token = token[:-1]
                if (len(token)==0): break
            # token with number stripped off
            token2.append(token)
            # add the number as the next item in the list
            token2.append(tmp)
        else:
            # no number at the end, so just put the token into our list
            token2.append(token)
        
    # update token list with what we just did
    tokens = token2.copy()

    # create an instance of the Note class for each token, then put each instance into a list called Notes
    Notes = []
    for token in tokens:
        note = Note(token, False, 0)           # 0 will mean we won't know absolute pitch number yet
        Notes.append(note)

    # fix abbreviations in the input:
    #       es -> ees
    #       as -> aes
    for n in Notes:
        if(leftMatch(n.token, "es")): 
            n.token = n.token.replace("es", "ees", 1)
        if (leftMatch(n.token, "as")):
            n.token = n.token.replace("as", "aas", 1)

     # now loop through the instances of our class...
    # figure out absolute number of each note...
    for n in Notes:
        token = n.token
   
        if leftMatch(token, "c"):
            n.is_note = True
            n.absolute_num = 48
           
        if leftMatch(token, "d"): 
            n.is_note = True
            n.absolute_num = 50
           
        if leftMatch(token, "e"):
            n.is_note = True
            n.absolute_num = 52
            
        if leftMatch(token, "f"):
            n.is_note = True
            n.absolute_num = 53
            
        if leftMatch(token, "g"):
            n.is_note = True
            n.absolute_num = 55

        if leftMatch(token, "a"): 
            n.is_note = True
            n.absolute_num = 57        
           
        if leftMatch(token, "b"): 
            n.is_note = True
            n.absolute_num = 59        
           
        num_commas = token.count(",")
        num_apostrophe = token.count("'")

        if (n.absolute_num > 0):
            if (num_commas > 0):
                n.absolute_num  = n.absolute_num - (12 * num_commas)
            elif (num_apostrophe > 0):
                n.absolute_num  = n.absolute_num + (12 * num_apostrophe)
    
    # do the transformation!
    for n in Notes:
        token = n.token

        if (n.is_note):

            # figure out new note name  
            if leftMatch(token, "a"): 
                n.new_name = "g"
            
            if leftMatch(token, "b"): 
                n.new_name = "f"
            
            if leftMatch(token, "c"):
                n.new_name = "e"
                
            if leftMatch(token, "d"): 
                n.new_name = "d"
            
            if leftMatch(token, "e"):
                n.new_name = "c"
                
            if leftMatch(token, "f"):
                n.new_name = "b"
                
            if leftMatch(token, "g"):
                n.new_name = "a" 

            # figure out new sharp/flat
            if (token.find("isis") > 0):
                n.new_name = n.new_name + "eses"
            elif (token.find("is") > 0):
                n.new_name = n.new_name + "es"
            elif (token.find("eses") > 0):
                n.new_name = n.new_name + "isis"
            elif (token.find("es") > 0):
                n.new_name = n.new_name + "is"

            # how high above splot_point (which must correspond to a A# or a D) is the original pitch?
            offset = (split_point - n.absolute_num);

            # make the new offset that much BELOW middle d...
            n.new_absolute = split_point + offset

            if (InRange(n.new_absolute, 0, 11)):
                n.new_name = n.new_name + ",,,,"
            if (InRange(n.new_absolute, 12, 23)):
                n.new_name = n.new_name + ",,,"
            if (InRange(n.new_absolute, 24, 35)):
                n.new_name = n.new_name + ",,"
            if (InRange(n.new_absolute, 36, 47)):
                n.new_name = n.new_name + ","
            if (InRange(n.new_absolute, 48, 59)):
               n.new_name = n.new_name + ""
            if (InRange(n.new_absolute, 60, 71)):
               n.new_name = n.new_name + "'"
            if (InRange(n.new_absolute, 72, 83)):
               n.new_name = n.new_name + "''"
            if (InRange(n.new_absolute, 84, 95)):
               n.new_name = n.new_name + "'''"
            if (InRange(n.new_absolute, 96, 107)):
               n.new_name = n.new_name + "''''"

    final_output = ""

    # loop through the list of Note instances, and print out each individual token
    for n in Notes:
        if n.is_note:
            t = n.new_name
        else:
            t = n.token
        
        final_output = final_output + " " + t 

    # put back on the original comment
    final_output = final_output + comment

    #???
    final_output = final_output[1:]

    # (other than spacing, it should be the same as our initial input)
    return(final_output)

def process_one_block(list):
      
        retval = ""

        for line in list:
            rawinput = line.rstrip()
            final_version = tokenize(rawinput)

            # in debug mode, we only report if the original input and our "reconstituted" output don't match...
            if (debug_mode and mode == 0):

                t1 = rawinput.replace(" ", "").strip()
                t2 = final_version.replace(" ", "").strip()

                if not (t1 == t2):
                    print("PROBLEM: ")
                    print(t1)
                    print(t2)
            else:
                #print(final_version.strip())
                if (retval == ""):
                    retval = final_version.strip()
                else:
                    retval = retval + "\n" + final_version.strip()

        return retval

# just return a string representation of a list, with line feeds between them 
def list_to_string(list):      
    retval = ""

    for line in list:
            if (retval == ""):
                retval = line.strip()
            else:
                retval = retval + "\n" + line.strip()

    return retval

# takes a string with carriage returns, and turns it into a list, one line per element
def string_to_list(s):
    retval = []
    tmp = s.split("\n")
    for t in tmp:
        retval.append(t)
    return retval

# taken an input key, and returns its mirror image
def mirror_image_key(original_key_letter, original_key_mode):
    retval = ""

    input_key_major = ["c", "g", "d", "a", "e", "b", "ces", "ges","fis", \
            "des", "cis", "aes", "ees", "bes", "f", "es"]
    
    # same NUMBER of sharps / flats as original key, but sharps instead of flats or vice versa
    output_key_major = ["c", "f", "bes", "ees", "aes", "des", \
            "cis", "fis", "ges", "b", "ces", "e", "a", "d", "g", "a"]

    input_key_minor = ["a", "e", "b", "fis", "cis", "gis", "ees", "dis","bes", \
            "f", "c", "g", "d"]
            
    output_key_minor = ["a", "d", "g", "c", "f", "bes", "dis", "ees","gis", \
            "cis", "fis", "b", "e"]

    # see if we are dealing with a major key
    if (original_key_mode.upper() == "MAJOR"):
        # if so, return the mirror image key
        for i in range(len(input_key_major)):
            if (original_key_letter.upper() == input_key_major[i].upper()):
                return output_key_major[i]
    else:
        # we are dealing with a minor key, return the mirror image key
        for i in range(len(input_key_minor)):
            if (original_key_letter.upper() == input_key_minor[i].upper()):
                return output_key_minor[i]
                
    # if we didn't find anything, it means there is some sort of logic error somewhere
    return "<error no key found> - " + original_key_letter + original_key_mode    

def wrap_in_quotes(input_str):
    return '"' + input_str + '"'

def to_ly_key(original_key_letter, original_key_mode):
    return "\\key " + original_key_letter + " \\" + original_key_mode

def to_ly_ottava(octave):
    return "\ottava #" + str(octave)

def to_half_step_string(num_steps):
    if (num_steps == 0): 
        return "N/A"
    else:
        return "Up " + str(num_steps) + " half steps"


# this function uses an external python script called "ly" to actually do the transposition
# write text out to temp file, wrapped in a variable
# insert the key sig
# execute ly, telling it to transpose the notes 
# read the output of ly back in
# and return the transposed notes, and the key sig that ly calculated
def transpose(text, original_key , original_mode, transposition_str):
    fd, path = mkstemp()

    # write out temp file-----------------------------------------
    with open(path, 'w') as f:
        #f.write('\language \"deutsch\"\n')      # this is to try to get LY from using abbreviations...
        f.write("block = {\n")
        f.write(to_ly_key(original_key, original_mode) + "\n")
        f.write(text + "\n")
        f.write("}\n")

    # close the file descriptor
    os.close(fd)

    input_file = path
    output_file = path + ".out"

    # execute LY--------------------------------------------------

    full_command = 'python ' + \
        wrap_in_quotes(ly_command) + ' ' + wrap_in_quotes('transpose ' +  transposition_str) + ' ' + wrap_in_quotes(input_file) + ' -o ' + wrap_in_quotes(output_file)

     # call LY on the temp file...
    os.system(full_command)

    # read back in file created by LY-----------------------------

    with open(output_file, 'r') as f:
        f.readline()                # skip first line we wrote out
        new_key = f.readline().split(" ")[1]                # grab the calculated key that LY figured out
        # then just read in the rest of the processed file
        full_file = ""
        tmp = ""
        while (not tmp == "}\n"):
            tmp = f.readline()
            if (not tmp == "}\n"):
                full_file = full_file + tmp

        new_key = new_key.strip()
        
        # it looks like the LY command outputs abbreviations using ES and AS for ees and aes, respectfully
        if (new_key == "es"):
            new_key = "ees"

        if (new_key == "as"):
            new_key = "aes"

        new_key = new_key.strip()

        return full_file, new_key.strip()

# right now, the only keys that are listed in here are the ones used by the inventions
# this needs updated to include all keys i think for other uses...
def half_steps_to_pitch_interval_1(key, mode, half_steps):
    retval = ""

    interval_1 = key
    interval_string = ""

    if (mode.upper() == "MAJOR"):
        #handle all major keys
        if (key == "c"): interval_string = "c cis d ees e f fis g aes a bes b"
        if (key == "g"): interval_string = "g aes a bes b c' cis' d' ees' e' f' fis'" 
        if (key == "d"): interval_string = "d ees e f fis g aes a bes b c' cis'"
        if (key == "a"): interval_string = "a bes b c' cis' d' ees' e' f' fis' g' aes'"
        if (key == "e"): interval_string = "e f fis g aes a bes b c' cis' d' ees'"
        if (key == "b"): interval_string = "b c' cis' d' ees' e' f' fis' g' gis' a ais'" 
        if (key == "ces"): interval_string = "ces c des d ees e f ges g aes a bes"
        if (key == "fis"): interval_string = "fis g gis a ais b c' cis' d' dis' e'" 
        if (key == "ges"): interval_string = "ges g aes a bes b c' des' d' ees' e' f'"
        if (key == "des"): interval_string = "des d ees e f ges g aes a bes b c'"  
        if (key == "cis"): interval_string = "cis d dis e f fis g gis a ais b"
        if (key == "aes"): interval_string = "aes a bes b c' des' d' ees' e' f' ges' g' a'" 
        if (key == "ees"): interval_string = "ees e f ges g aes a bes b c' des' d'"      
        if (key == "bes"): interval_string = "bes c' des' d' ees' e' f' ges' g' aes' a' b"        
        if (key == "f"): interval_string = "f ges g aes a bes b c' des' d' ees' e'"           
            

    else:
        #handle all minor keys
        if (key == "a"): interval_string = "a bes b c' des' d' ees' e' f' ges' g' aes'"
        if (key == "e"): interval_string = "e f fis g gis a bes b c' cis' d' dis'"
        if (key == "b"): interval_string = "b c' cis' d' dis' e' f' fis' g' gis' a' ais'"
        if (key == "fis"): interval_string = "fis g gis a ais b c' cis' d' dis' e' f'"
        if (key == "cis"): interval_string = "cis d dis e f fis g gis a ais b c'"
        if (key == "gis"): interval_string = "gis a ais b c' cis' d' dis' e' f' fis' g'" 
        if (key == "ees"): interval_string = "ees e f ges g aes a bes b c' des' d'"
        if (key == "dis"): interval_string = "dis e f fis g gis a ais b c' cis' d'"            
        if (key == "bes"): interval_string = "bes b c' des' d' ees' e' f' ges' g' aes' a'"
        if (key == "f"): interval_string = "f ges g aes a bes b c' des' d' ees' e'"
        if (key == "c"): interval_string = "c des d ees e f ges g aes a bes b"
        if (key == "g"): interval_string = "g aes a bes b c' des' d' ees' e' f' ges'"
        if (key == "d"): interval_string = "d ees e f ges g aes a bes b c' des'"   

            
    if (interval_string == ""):
        print("INVALID KEY DETECTED")
        exit(1)
        
    interval_2 = interval_string.split(' ')[half_steps]

    # make sure the key exists; if not it is a theoretical key, so just substitute its enharmonic equivalent
    if (mode.upper() == "MAJOR"):
        x = 1
    else:
        if (leftMatch(interval_2, "ges")): interval_2 = "fis"             # gflat minor doesn't exist... convert to f# minor
        if (leftMatch(interval_2, "aes")): interval_2 = "gis"             # aflat minor doesn't exist... convert to g# minor
        if (leftMatch(interval_2, "des")): interval_2 = "cis"             # dflat minor doesn't exist... convert to c# minor
        if (leftMatch(interval_2, "ais")): interval_2 = "bes"             # asharp minor doesn't exist... convert to bflat minor

    
    retval = interval_1 + " " + interval_2

    return retval

# takes a string like this:
#   /option=value
# and returns value as a number
def process_number(input,option):
    retval = ""

    # make sure they specified the option we are looking for 
    if (input.upper().find(option.upper()) == -1):
        print('problem: ' + input.upper() + ' ' + option.upper())
        exit()

    tmp = input.split("=")          
    retval = int(tmp[1])

    return retval

def print_help():
    help = """
mozart-compile: a compiler for creating mirror image scores
Benjamin Pritchard / Kundalini Software

Usage:
    mozart-compile /transpose=X /split=X /mode=X input_file output_file  

notes:
    /transpose means number of half steps to transpose, must be between 0 and 11, inclusive
    /split means where to split the keyboard, when generating mirror image notes. use X or middle d, X for A# below middle d, or X for A# above middle d.
    /modes means:
        0 no mirroring
        l Left Hand Ascending
        2 Right Hand Ascending
        3 Mirror
        4 Left Hand Ascending Call Response
        5 Right Hand Ascending Call Response

All command line parameters are required, and must be specified in order.
Python package python_ly must be installed for this to work

Example:
    mozart-compile /transpose=1 /split=56 /mode=0 input_file output_file
"""
    print(help)    
    exit()

#---------------------------------------------------------------------------
# main program begins here

if (len(sys.argv) == 1): 
    half_steps_to_transpose = 5
    split_point = 56
    mode = 1 

    input_file = 'C:\\kundalini\\bach inventions\\mozart-transpose-input\\01.ly'
    output_file = 'C:\\kundalini\\bach inventions\\mozart-transpose-output\\01.ly'
else:
    if (len(sys.argv) != 6):
        print_help()

    half_steps_to_transpose = process_number(sys.argv[1], "/transpose")
    split_point = process_number(sys.argv[2], "/split")
    mode = process_number(sys.argv[3], "/mode")

    input_file = sys.argv[4]
    output_file = sys.argv[5]

print("Mozart Compile, version " + Version_String)
print("Written by Benjamin Pritchard / Kundalini Software")
print("half_steps_to_transpose =  " + str(half_steps_to_transpose))
print("split_point = " + str(split_point))
print("mode = " + str(mode))
print("input_file = " + input_file)
print("output_file = " + output_file)

with open(input_file) as fp:

    composer = fp.readline().rstrip()
    title = fp.readline().rstrip() 
    opus = fp.readline().rstrip() 

    original_key_line = fp.readline().rstrip()
    tmp = original_key_line.split(" ")

    original_key_letter = tmp[0]
    original_key_mode   = tmp[1]

    # time sig should always be the same
    time = fp.readline().rstrip()
    time_1 = time
    time_2 = time
    
    # skip blank line
    fp.readline()

    voiceone_line = fp.readline().rstrip()
    bracket = fp.readline().rstrip()

    voice_one = []
    done = False
    while (not done):
        tmp = fp.readline().rstrip()
        if (tmp != "}"):
            voice_one.append(tmp)
        else:
            done = True

    # skip blank line        
    fp.readline()
    
    voicetwo_line = fp.readline().rstrip()
    bracket = fp.readline().rstrip()

    voice_two = []
    done = False
    while (not done):
        tmp = fp.readline().rstrip()
        if (tmp != "}"):
            voice_two.append(tmp)
        else:
            done = True

# now create our output!!
# the following line can be added to the header if 
#     tagline           = \markup { \with-url #"https://www.kundalinisoftware.com/bach-in-the-mirror/" { www.kundalinisoftware.com/bach-in-the-mirror/ } }

output_template = """
\header{
    composer          = \"{composer}\"
    title             = \"{title}\"
    tagline           = ""
}

\\version "2.18.2"

voiceone =  {
    {key_1}
    {time_1}
    \\clef "treble"
    {ottava_1}
    {voice_one_block}
}

voicetwo = {
    {key_2}
    {time_2}
    \\clef "bass"
    {ottava_2}
    {voice_two_block}
}

\markup {
  {mode_string}
}

\markup {
  Transposition: {half_step_transposition}
}

\markup {
  Split: {split}
}

\score {
    \context PianoStaff <<
        \context Staff = \"one\" << \\voiceone >>
        \context Staff = \"two\" << \\voicetwo >>
    >>

\layout { }

}

"""

split_string = str(split_point)

# no transposition
if (mode == 0):
    print("no mirroring")
    octave_1 = 0
    octave_2 = 0
    mode_string = "No Mirroring"
    splt_string = "N/A"

    # two keys should be the same
    # two modes will be the same 
    key_1 = original_key_letter                                                       
    key_2 = original_key_letter

    voice_one_block = list_to_string(voice_one)
    voice_two_block = list_to_string(voice_two)

    transposition_str = half_steps_to_pitch_interval_1(key_1, original_key_mode, half_steps_to_transpose)

    voice_one_block, new_key_1 = transpose(voice_one_block, key_1, original_key_mode, transposition_str)
    voice_two_block, new_key_2 = transpose(voice_two_block, key_2, original_key_mode, transposition_str)

    # the transpose function above returns us the new key 
    key_1 = new_key_1   
    key_2 = new_key_2   

    ottava_1 = to_ly_ottava(octave_1)
    ottava_2 = to_ly_ottava(octave_2)

#Left Hand Ascending
if (mode == 1): 
    octave_1 = 0
    octave_2 = 0
    mode_string =  "Left Hand Ascending"
    key_1 = original_key_letter
    key_2 = mirror_image_key(original_key_letter, original_key_mode)                # key_2 will have same mode as key_1 always

    transposition_str = half_steps_to_pitch_interval_1(key_1, original_key_mode, half_steps_to_transpose)

    voice_one_block = list_to_string(voice_one)
    voice_one_block, new_key_1 = transpose(voice_one_block, key_1, original_key_mode, transposition_str)

    voice_two_block = process_one_block(string_to_list(voice_one_block))

    # in the mirror image notes that we generated, get rid of any clef changes from the original input
    voice_two_block = voice_two_block.replace("\clef \"bass\"", "")
    voice_two_block = voice_two_block.replace("\clef \"treble\"", "")

    # the transpose function above returns us the new key 
    key_1 = new_key_1   
    key_2 = mirror_image_key(new_key_1, original_key_mode)   

    ottava_1 = to_ly_ottava(octave_1)
    ottava_2 = to_ly_ottava(octave_2)

#Right Hand Descending
if (mode == 2): 
    octave_1 = 0
    octave_2 = 0
    mode_string = "Right Hand Descending"
    key_1 = mirror_image_key(original_key_letter, original_key_mode)
    key_2 = original_key_letter

    transposition_str = half_steps_to_pitch_interval_1(key_1, original_key_mode, half_steps_to_transpose)

    # do our transpostions
    voice_one_block = process_one_block(voice_two)  
    voice_one_block, new_key_1 = transpose(voice_one_block, key_1, original_key_mode, transposition_str)

    voice_two_block = process_one_block(string_to_list(voice_one_block))

    # in the mirror image notes that we generated, get rid of any clef changes from the original input
    voice_one_block = voice_one_block.replace("\clef \"bass\"", "")
    voice_one_block = voice_one_block.replace("\clef \"treble\"", "")

    # the transpose function above returns us the new key 
    key_1 = new_key_1   
    key_2 = mirror_image_key(new_key_1, original_key_mode)   

    ottava_1 = to_ly_ottava(octave_1)
    ottava_2 = to_ly_ottava(octave_2)

#Mirror Image
if (mode == 3): 
    octave_1 = -1
    octave_2 = -1
    mode_string = "Mirror Image"
    key_1 = mirror_image_key(original_key_letter, original_key_mode)
    key_2 = mirror_image_key(original_key_letter, original_key_mode)

    transposition_str = half_steps_to_pitch_interval_1(key_1, original_key_mode, half_steps_to_transpose)

    # do our transpostions
    voice_one_block = process_one_block(voice_two)        
    voice_one_block, new_key_1 = transpose(voice_one_block, key_1, original_key_mode, transposition_str)

    voice_two_block = process_one_block(voice_one)
    voice_two_block, new_key_2 = transpose(voice_two_block, key_2, original_key_mode, transposition_str)

    # in the mirror image notes that we generated, get rid of any clef changes from the original input
    voice_one_block = voice_one_block.replace("\clef \"bass\"", "")
    voice_one_block = voice_one_block.replace("\clef \"treble\"", "")

    # in the mirror image notes that we generated, get rid of any clef changes from the original input
    voice_two_block = voice_two_block.replace("\clef \"bass\"", "")
    voice_two_block = voice_two_block.replace("\clef \"treble\"", "")

    # the transpose function above returns us the new key 
    key_1 = new_key_1   
    key_2 = new_key_2   

    ottava_1 = to_ly_ottava(octave_1)
    ottava_2 = to_ly_ottava(octave_2)

output_template = output_template.replace("{composer}", composer)
output_template = output_template.replace("{title}", title + ", " + opus)
#output_template = output_template.replace("{opus}", opus)

output_template = output_template.replace("{mode_string}", mode_string)
output_template = output_template.replace("{split}", split_string)
output_template = output_template.replace("{half_step_transposition}", to_half_step_string(half_steps_to_transpose))

output_template = output_template.replace("{key_1}", to_ly_key(key_1, original_key_mode))               # major/minor doesn't change
output_template = output_template.replace("{time_1}", time_1)
output_template = output_template.replace("{ottava_1}", to_ly_ottava(octave_1))
output_template = output_template.replace("{voice_one_block}", voice_one_block)

output_template = output_template.replace("{key_2}", to_ly_key(key_2, original_key_mode))               # major/minor doesn't change
output_template = output_template.replace("{time_2}", time_2)
output_template = output_template.replace("{ottava_2}", to_ly_ottava(octave_2))
output_template = output_template.replace("{voice_two_block}", voice_two_block)

# certain things mess up our parsing logic, such as:
#   \times 2/3
#
# so i created a workaround:
#   \times 2/3@
#
# which prevents our parsing logic from breaking the 2/3 up into tokens
output_template = output_template.replace("@", " ")

with open(output_file, "w+") as fp:
    fp.write(output_template)