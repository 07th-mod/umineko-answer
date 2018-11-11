import re
import os


#these error strings appear when the 0.utf/0.u cannot be found
defaultErrorString = b'No game script found. This application must be run from a directory containing NScripter, ONScripter, or Ponscripter game data.'

def getNewErrorString():
    newErrorString = b"ERROR (07th mod): The script file '0.u' is missing from the game directory. You probably forgot to rename '0.utf' to '0.u'."

    if len(newErrorString) > len(defaultErrorString):
        print('ERROR: replacement string is longer than original string!')
        print('Original:    ' + str(defaultErrorString))
        print('Replacement: ' + str(newErrorString))
        exit(-1)

    #pad new error string with null characters until it's the same length
    padding_required = len(defaultErrorString) - len(newErrorString)
    newErrorStringPadded = newErrorString + (b'\x00' * padding_required)

    #sanity check
    if len(newErrorStringPadded) != len(defaultErrorString):
        print('coding error - string lengths should be the same!')

    return newErrorStringPadded

def get_input_files() -> [str]:
    file_paths_to_process = []

    for filename_any_case in os.listdir('.'):
        filename = filename_any_case.lower()
        root, ext = os.path.splitext(filename)
        if filename in ['umineko1to4', 'umineko1to4.exe', 'umineko5to8', 'umineko5to8.exe', 'umineko4', 'umineko8']:
            file_paths_to_process.append(filename)

    return file_paths_to_process

########################################################################################################################

print('Patching the following files:', get_input_files())

for file_to_patch in get_input_files():
    print('\n\nBegin Patching', file_to_patch)
    with open(file_to_patch, "rb") as f:
        exe_byte_array = f.read()

        #these will have a null character (\x00) appended to them before the replacement is performed
        string_replacements_required = [
        (defaultErrorString, getNewErrorString(), 1),
        ]

        for before_string, after_string, max_replacements in string_replacements_required:
            #check number of time of the search string occurs in the file, as a check
            num_ocurrances = len(re.findall(before_string + b'\x00', exe_byte_array))

            (exe_byte_array, num_replacements) = re.subn(re.escape(before_string + b'\x00'), after_string + b'\x00', exe_byte_array, count=max_replacements)
            print('Replaced String {} to {} {} times (occurs {} times in file)'.format(before_string, after_string, num_replacements, num_ocurrances))
            if num_replacements == 0:
                print("Error: couldn't patch {} string to {}".format(before_string, after_string))
                exit(0)
                

    #save the file to disk only if all the above patches were successful
    savedir = 'patched'
    os.makedirs(savedir, exist_ok=True)
    with open(os.path.join(savedir,file_to_patch), 'wb') as outFile:
        outFile.write(exe_byte_array)
        print("----------------")
        print("Finished, wrote to:", outFile.name)

print('The patched .exes will now have the new warning message.')

#notes:
#Please see the function "int ScriptHandler::readScript(DirPaths *path, const char* prefer_name)" in ScriptHandler.cpp of Ponscripter
# the extra changes are necessary due to how the game scans for script files - it will always (mostly always) scan for 0.utf, 1.utf 2 ... and also 00.utf, 01.utf etc
# The filename must be included in the scan range, hence the modification to search for 0.ut, 1.ut ... instead of 00.utf, 01.utf ....
#
# On linux only, I noticed the '0.utf' string and the '00.utf' string are compressed together so you only see '00.utf' in the binary.
# I think the patch will still work anyway.
