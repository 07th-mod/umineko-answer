import os
import re, hashlib, struct
import sys
from typing import List, Tuple
from enum import Enum


def sha256(byte_array):
    m = hashlib.sha256()
    m.update(byte_array)
    return m.hexdigest()


class OperatingSystem(Enum):
    WINDOWS = 1
    LINUX = 2
    MACOS = 3


def printUsageInstructions():
    print('USAGE INSTRUICTIONS GO HERE')


def read_file(path):
    with open(path, "rb") as f:
        return f.read()


def write_file(path, file_data):
    with open(path, 'wb') as outFile:
        outFile.write(file_data)


def get_instruction_string(arr, offset = 0):
    return ' '.join(['{:02x}'.format(b) for b in arr[offset:offset + 5]])


def print_instruction(arr, offset):
    print(get_instruction_string(arr, offset))


def print_replacement_details(width_pattern, height_pattern, new_width_pattern, new_height_pattern):
    print("\tWidth : [{}] -> [{}]".format(get_instruction_string(width_pattern), get_instruction_string(new_width_pattern)))
    print("\tHeight: [{}] -> [{}]".format(get_instruction_string(height_pattern), get_instruction_string(new_height_pattern)))


def patch_resolution(exe_byte_array, width, height, is_macos):
    print("Trying to patch resolution to {}x{}. Changes:".format(width, height))

    if is_macos:
        return patch_resolution_macos(exe_byte_array, width, height)
    else:
        return patch_resolution_windows_linux(exe_byte_array, width, height)


def patch_resolution_macos(exe_byte_array, width, height):
    """
    # see https://github.com/07th-mod/umineko-question/issues/19#issuecomment-254448715 for details on MacOS version
    """

    # target instructions to be modified
    height_pattern = b'\x66\xb9' + struct.pack('H', 960)
    width_pattern = b'\x66\xb8' + struct.pack('H', 1280)

    # calculate what the new instructions should be
    new_height_pattern = b'\x66\xb9' + struct.pack('H', height)
    new_width_pattern = b'\x66\xb8' + struct.pack('H', width)

    print_replacement_details(width_pattern, height_pattern, new_width_pattern, new_height_pattern)

    # substitute the old byte sequence with the new byte sequence. Only replace the first instance
    (exe_byte_array, n_height_subs) = re.subn(re.escape(height_pattern), new_height_pattern, exe_byte_array, count=1)
    if n_height_subs != 1:
        raise Exception("Error: couldn't patch set height instruction!")

    (exe_byte_array, n_width_subs) = re.subn(re.escape(width_pattern), new_width_pattern, exe_byte_array, count=1)
    if n_width_subs != 1:
        raise Exception("Error: couldn't patch set width instruction!")

    return exe_byte_array


def patch_resolution_windows_linux(exe_byte_array, width, height):
    """
    sequence of instructions can be decoded at https://defuse.ca/online-x86-assembler.htm#disassembly
    mov edx, 960
    mov ecx, 1280
    BA C0030000   -> mov edx, 0x03c0 (note immediate operand is little-endian for x86)
    B9 00050000   -> mov ecx, 0x0500
    or reference, expected values for 1920 x 1080 are: width: 80 07 00 00, height: 38 04 00 00

    :param exe_byte_array: raw byte array
    :param width: new width for the .exe
    :param height: new height for the .exe
    :return: the patched exe as raw bytes
    """
    # target instructions to be modified
    height_pattern = b'\xBA\xC0\x03\x00\x00'
    width_pattern = b'\xB9\x00\x05\x00\x00'

    # calculate what the new instructions should be
    new_height_pattern = b'\xBA' + height.to_bytes(4, 'little')
    new_width_pattern = b'\xB9' + width.to_bytes(4, 'little')

    #calculate sha1 of the exe and check if it is as expected. if not, possibly different .exe version but will still work
    m = hashlib.sha1()
    m.update(exe_byte_array)

    print_replacement_details(width_pattern, height_pattern, new_width_pattern, new_height_pattern)

    #substitute the old byte sequence with the new byte sequence. Only replace the first instance
    (exe_byte_array, n_height_subs) = re.subn(re.escape(height_pattern), new_height_pattern, exe_byte_array, count=1)
    if n_height_subs != 1:
        raise Exception("Error: couldn't patch set height instruction!")

    (exe_byte_array, n_width_subs) = re.subn(re.escape(width_pattern), new_width_pattern, exe_byte_array, count=1)
    if n_width_subs != 1:
        raise Exception("Error: couldn't patch set width instruction!")

    return exe_byte_array


def patch_strings(exe_byte_array, string_replacements_required: List[Tuple[bytes, bytes, int]]):
    # Each item in string_replacements_required will have a null character (\x00) appended to them
    # before the replacement is performed

    for before_string, after_string, max_replacements in string_replacements_required:
        # check number of time of the search string occurs in the file, as a check
        num_ocurrances = len(re.findall(before_string + b'\x00', exe_byte_array))

        (exe_byte_array, num_replacements) = re.subn(re.escape(before_string + b'\x00'), after_string + b'\x00',
                                                     exe_byte_array, count=max_replacements)
        print('Replaced String {} to {} {} times (occurs {} times in file)'.format(before_string, after_string,
                                                                                   num_replacements,
                                                                                   num_ocurrances))
        if num_replacements == 0:
            raise Exception("Error: couldn't patch {} string to {}".format(before_string, after_string))

    return exe_byte_array


def patch_warning_message(exe_byte_array):
    # These error strings are displayed by the game .exe when the 0.utf/0.u file cannot be found
    default_error_string = b'No game script found. This application must be run from a directory containing NScripter, ONScripter, or Ponscripter game data.'

    def get_new_error_string():
        new_error_string = b"ERROR (07th mod): The script file '0.u' is missing from the game directory. You probably forgot to rename '0.utf' to '0.u'."

        if len(new_error_string) > len(default_error_string):
            raise Exception('ERROR: replacement string is longer than original string!' +
                            '\nOriginal:    ' + str(default_error_string) +
                            '\nReplacement: ' + str(new_error_string))

        # pad new error string with null characters until it's the same length
        padding_required = len(default_error_string) - len(new_error_string)
        new_error_string_padded = new_error_string + (b'\x00' * padding_required)

        # sanity check
        if len(new_error_string_padded) != len(default_error_string):
            raise Exception('coding error - string lengths should be the same!')

        return new_error_string_padded

    return patch_strings(exe_byte_array, [(default_error_string, get_new_error_string(), 1)])


def patch_saves_mysav(exe_byte_array):
    return patch_strings(exe_byte_array, [(b'saves/', b'mysav/', 2)])


# Notes:
# Please see the function "int ScriptHandler::readScript(DirPaths *path, const char* prefer_name)" in
# ScriptHandler.cpp of Ponscripter
# the extra changes are necessary due to how the game scans for script files - it will always (mostly always)
# scan for 0.utf, 1.utf 2 ... and also 00.utf, 01.utf etc
# The filename must be included in the scan range, hence the modification to search for 0.ut, 1.ut ...
# instead of 00.utf, 01.utf ....
# On linux only, I noticed the '0.utf' string and the '00.utf' string are compressed together so you only
# see '00.utf' in the binary.
# I think the patch will still work anyway.
def patch_load_0u(exe_byte_array):
    string_replacements_required = [
        (b'0.utf', b'0.u\x00\x00', 1),  # this forces game to check for '0.ut', and only run if that file exists
        (b'%d.%s', b'%dx%s', 1),  # this prevents 0.utf being loaded
        (b'%02d.%s', b'%d.%.1s', 1),
        # this loads the files 0.ut, 1.ut, 2.ut ...
        # TODO: Is it valid to have %.1s ? %1s is valid, but %.1s doesn't seem to be....
    ]

    return patch_strings(exe_byte_array, string_replacements_required)


def patch_umineko_video_windows(exe_byte_array):
    lea_pattern = b'\xFF\xFF\x8D\x44\x00\x04'

    # calculate what the new instructions should be
    new_lea_pattern = b'\xFF\xFF\x90\x90\x90\x90'  # replace with NOP

    # substitute the old byte sequence with the new byte sequence. Only replace the first instance
    (exe_byte_array, n_height_subs) = re.subn(re.escape(lea_pattern), new_lea_pattern, exe_byte_array, count=2)
    print('Replacements Made:', n_height_subs)
    if n_height_subs != 2:
        raise Exception("Error: couldn't patch video res!")

    return exe_byte_array


def patch_umineko_video_windows_new_question_arcs(exe_byte_array):
    # Original Version:
    # .text:0044A68C                 call    SDL_UpdateTexture
    # .text:0044A691                 mov     ecx, [ebp+var_128]
    # .text:0044A697                 mov     [esp+1A8h+var_1A0], esi
    # .text:0044A69B                 mov     [ebp+var_A8], 2      //load 2 (the video offset)
    # .text:0044A6A5                 mov     [ebp+var_A4], 2      //load 2 (the video offset)
    # .text:0044A6AF                 lea     eax, [ecx+ecx]       //multiply by 2 of ecx into eax (should be 8d 04 09)
    # .text:0044A6B2                 mov     ecx, [ebp+var_124]
    # .text:0044A6B8                 mov     [ebp+var_A0], eax
    # .text:0044A6BE                 lea     eax, [ecx+ecx]       //multiply by 2 of ecx into eax (should be 8d 04 09)
    # .text:0044A6C1                 mov     [ebp+var_9C], eax
    # .text:0044A6C7                 lea     eax, [ebp+var_A8]
    # .text:0044A6CD                 mov     [esp+1A8h+var_19C], eax
    # .text:0044A6D1                 mov     eax, ds:dword_786130
    # .text:0044A6D6                 mov     [esp+1A8h+var_1A4], eax
    # .text:0044A6DA                 mov     eax, [ebp+var_164]
    # .text:0044A6E0                 mov     eax, [eax+0D00h]
    # .text:0044A6E6                 mov     [esp+1A8h+var_1A8], eax
    # .text:0044A6E9                 call    SDL_RenderCopy
    #
    # Updated Version:
    # .text:0044A68C                 call    SDL_UpdateTexture
    # .text:0044A691                 mov     ecx, [ebp+var_128]
    # .text:0044A697                 mov     [esp+1A8h+var_1A0], esi
    # .text:0044A69B                 mov     [ebp+var_A8], 2
    # .text:0044A6A5                 mov     [ebp+var_A4], 2
    # .text:0044A6AF                 lea     eax, [ecx+ecx]       //change to just ecx NOP(should be 8d 01 90) (90 is NOP)
    # .text:0044A6B2                 mov     ecx, [ebp+var_124]
    # .text:0044A6B8                 mov     [ebp+var_A0], eax
    # .text:0044A6BE                 lea     eax, [ecx+ecx]       //change to just ecx NOP(should be 8d 01 90)
    # .text:0044A6C1                 mov     [ebp+var_9C], eax
    # .text:0044A6C7                 lea     eax, [ebp+var_A8]
    # .text:0044A6CD                 mov     [esp+1A8h+var_19C], eax
    # .text:0044A6D1                 mov     eax, ds:dword_786130
    # .text:0044A6D6                 mov     [esp+1A8h+var_1A4], eax
    # .text:0044A6DA                 mov     eax, [ebp+var_164]
    # .text:0044A6E0                 mov     eax, [eax+0D00h]
    # .text:0044A6E6                 mov     [esp+1A8h+var_1A8], eax
    # .text:0044A6E9                 call    SDL_RenderCopy

    # This file patches the new Umineko1to4.exe to use full size videos. The PonscripterLabel_sound.cpp file has been changed, so the method of patching has changed too.
    # In the future, open the .exe in IDA, lookup a known function (like SDL_RenderCopy), press X to chart xrefs to, and check all the xrefs.

    # these bytes control the video offset
    # controls the video offset (r2.x/y in the file PonscripterLabel_sound.cpp):
    # leaPattern = re.escape(b'\xC7\x85\x58\xFF\xFF\xFF\x02\x00\x00\x00\xC7\x85\x5C\xFF\xFF\xFF\x02\x00\x00\x00') - this controls the video pixel offset, currently set to 2pix

    # NOTE: before  re.escape was not used, which may have led to incorrect behavior depeding on the replacement string...this has now been fixed
    lea_pattern = re.escape(b'\x8d\x04\x09\x8b\x8d\xdc\xfe\xff\xff\x89\x85\x60\xff\xff\xff\x8d\x04\x09')

    # calculate what the new instructions should be
    new_lea_pattern = b'\x8d\x01\x90\x8b\x8d\xdc\xfe\xff\xff\x89\x85\x60\xff\xff\xff\x8d\x01\x90'  # replace with NOP

    # substitute the old byte sequence with the new byte sequence. Only replace the first instance
    (exe_byte_array, n_height_subs) = re.subn(lea_pattern, new_lea_pattern, exe_byte_array, count=2)
    print('Replacements Made:', n_height_subs)
    if n_height_subs != 1:
        raise Exception("Error: couldn't patch video res!")

    return exe_byte_array

# The following two functions for patching the video res on linux/mac don't work properly
# we currently just ship a half-res video for Linux/MacOS, and the full res video only for Windows
# def patch_umineko_video_linux_NOT_WORKING(exe_byte_array):
#     leaPattern = b'\x8D\x44\x00\x04'
#
#     # calculate what the new instructions should be
#     newLeaPattern = b'\x90\x90\x90\x90'  # replace with NOP
#
#     print('NOTE - Use the windows widescreen patcher to get 1080p Resolution for the linux executable\n\n')
#
#     # for linux_skip the first 352676 bytes to ignore an incorrect match
#     start_of_exe = exe_byte_array[:352576]
#     area_to_patch = exe_byte_array[352576:]
#
#     # substitute the old byte sequence with the new byte sequence. Only replace the first instance
#     (area_to_patch, n_height_subs) = re.subn(re.escape(leaPattern), newLeaPattern, area_to_patch)
#     print('Replacemnts Made:', n_height_subs)
#     if n_height_subs != 2:
#         print("Error: couldn't patch set height instruction!")
#         exit(0)
#
#     return start_of_exe + area_to_patch
#
# def patch_umineko_video_macos_NOT_WORKING(exe_byte_array):
#     leaPattern = b'\x8D\x44\x00\x04'
#
#     # calculate what the new instructions should be
#     newLeaPattern = b'\x90\x90\x90\x90'  # replace with NOP
#
#     # substitute the old byte sequence with the new byte sequence. Only replace the first instance
#     (exe_byte_array, n_height_subs) = re.subn(re.escape(leaPattern), newLeaPattern, exe_byte_array)
#     print('Replacemnts Made:', n_height_subs)
#     if n_height_subs != 2:
#         print("Error: couldn't patch set height instruction!")
#         exit(0)
#
#     return exe_byte_array


# Linux patches:
# - patch resolution to 1080p
# - patch warning message
# - patch 0.utf -> 0.u
# - patch saves -> mysav (consider removing this in the future)
# - note: video patch is NOT performed for linux .exe!
def all_patch_linux(exe_byte_array, width, height):
    exe_byte_array = patch_resolution(exe_byte_array, width, height, is_macos=False)
    exe_byte_array = patch_warning_message(exe_byte_array)
    exe_byte_array = patch_load_0u(exe_byte_array)
    exe_byte_array = patch_saves_mysav(exe_byte_array)
    return exe_byte_array


# Macos patches:
# - patch resolution to 1080p
# - patch warning message
# - patch 0.utf -> 0.u
# - patch saves -> mysav (consider removing this in the future)
# - note: video patch is NOT performed for macos .exe!
def all_patch_macos(exe_byte_array, width, height):
    exe_byte_array = patch_resolution(exe_byte_array, width, height, is_macos=True)
    exe_byte_array = patch_warning_message(exe_byte_array)
    exe_byte_array = patch_load_0u(exe_byte_array)
    exe_byte_array = patch_saves_mysav(exe_byte_array)
    return exe_byte_array


# Windows patches:
# - patch resolution to 1080p
# - patch warning message
# - patch 0.utf -> 0.u
# - patch saves -> mysav (consider removing this in the future)
# - patch video resolution so video is not doubled in size
def all_patch_windows(exe_byte_array, width, height, new_question_arcs_video_patch):
    exe_byte_array = patch_resolution(exe_byte_array, width, height, is_macos=False)
    exe_byte_array = patch_warning_message(exe_byte_array)
    exe_byte_array = patch_load_0u(exe_byte_array)
    exe_byte_array = patch_saves_mysav(exe_byte_array)
    if new_question_arcs_video_patch:
        exe_byte_array = patch_umineko_video_windows_new_question_arcs(exe_byte_array)
    else:
        exe_byte_array = patch_umineko_video_windows(exe_byte_array)

    return exe_byte_array


def main():
    if len(sys.argv) < 2:
        printUsageInstructions()
        raise("Not enough arguments")

    exe_path = sys.argv[1]
    exe_filename = os.path.basename(exe_path)

    linux_filenames = ['Umineko1to4', 'Umineko5to8']
    windows_filenames = ['Umineko1to4.exe', 'Umineko5to8.exe']
    macos_filenames = ['umineko4', 'umineko8']

    operating_system = None
    if exe_filename in linux_filenames:
        operating_system = OperatingSystem.LINUX
    elif exe_filename in windows_filenames:
        operating_system = OperatingSystem.WINDOWS
    elif exe_filename in macos_filenames:
        operating_system = OperatingSystem.MACOS
    else:
        raise Exception(f"Unknown exe type - exe name '{exe_filename}' is unknown")

    print(f"Loading exe [{exe_path}]")
    exe_byte_array = read_file(exe_path)

    new_width = 1920
    new_height = 1080

    if operating_system == OperatingSystem.LINUX:
        patched_exe_byte_array = all_patch_linux(exe_byte_array, new_width, new_height)
    elif operating_system == OperatingSystem.MACOS:
        patched_exe_byte_array = all_patch_macos(exe_byte_array, new_width, new_height)
    elif operating_system == OperatingSystem.WINDOWS:
        raise NotImplemented("I haven't sorted out the 'new_question_arcs_video_patch' mode setting automatically - this still needs to be done, or just try both and see which one works")
        patched_exe_byte_array = all_patch_windows(exe_byte_array, new_width, new_height, new_question_arcs_video_patch)
    else:
        raise Exception(f"Patching os {operating_system} not implemented")

    write_file(exe_path + '.patched', patched_exe_byte_array)

    print(f"Patched exe from [{sha256(exe_byte_array)}] (orignal) to [{sha256(patched_exe_byte_array)}] (patched)", )


if __name__ == '__main__':
    main()
