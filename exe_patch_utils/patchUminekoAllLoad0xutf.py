import re
import os

def get_input_files() -> [str]:
    file_paths_to_process = []

    for filename_any_case in os.listdir('.'):
        filename = filename_any_case.lower()
        root, ext = os.path.splitext(filename)
        if filename in ['umineko1to4', 'umineko1to4.exe', 'umineko5to8', 'umineko5to8.exe', 'umineko4', 'umineko8']:
            file_paths_to_process.append(filename)

    return file_paths_to_process

print('Patching the following files:', get_input_files())

for file_to_patch in get_input_files():
    with open(file_to_patch, "rb") as f:
        exe_byte_array = f.read()

        #these will have a null character (\x00) appended to them before the replacement is performed
        string_replacements_required = [
        (b'0.utf', b'0.u\x00\x00'),  #this forces game to check for '0.ut', and only run if that file exists
        (b'%d.%s', b'%dx%s'),     #this prevents 0.utf being loaded
        (b'%02d.%s', b'%d.%.1s'), #this loads the files 0.ut, 1.ut, 2.ut ...
        ]

        for before_string, after_string in string_replacements_required:
            (exe_byte_array, num_replacements) = re.subn(before_string + b'\x00', after_string + b'\x00', exe_byte_array, count=1)
            print('Replaced String {} to {} {} times'.format(before_string, after_string, num_replacements))
            if num_replacements != 1:
                print("Error: couldn't patch {} string to {}", before_string, after_string)
                exit(0)


    #save the file to disk only if all the above patches were successful
    with open('run_u_ext_' + file_to_patch, 'wb') as outFile:
        outFile.write(exe_byte_array)
        print("----------------")
        print("Finished, wrote to:", outFile.name)

print('The patched .exes will now launch "0.u" instead of "0.utf".')

#notes:
#Please see the function "int ScriptHandler::readScript(DirPaths *path, const char* prefer_name)" in ScriptHandler.cpp of Ponscripter
# the extra changes are necessary due to how the game scans for script files - it will always (mostly always) scan for 0.utf, 1.utf 2 ... and also 00.utf, 01.utf etc
# The filename must be included in the scan range, hence the modification to search for 0.ut, 1.ut ... instead of 00.utf, 01.utf ....
