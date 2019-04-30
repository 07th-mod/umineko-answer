from __future__ import annotations
import glob
import os
from util import get_with_file_extension

def splitByNumber(s):
    # the first position is always assumed to be a alpha
    inDigit = False

    chunks = []
    currentChunk = []
    for c in s:
        if inDigit:
            if c.isdigit():
                currentChunk.append(c)
            else:
                chunks.append(currentChunk)
                currentChunk = [c]
                inDigit = False
        else:
            if c.isdigit():
                chunks.append(currentChunk)
                currentChunk = [c]
                inDigit = True
            else:
                currentChunk.append(c)

    if currentChunk:
        chunks.append(currentChunk)

    return [''.join(x) for x in chunks]


#splits a name and converts to lower case
def splitName(s):
    splitName = s.split('_')
    nameStart = splitName[0]
    nameEnd = '' if len(splitName) == 1 else splitName[1]

    s = splitByNumber(nameEnd)
    return nameStart.lower(), s

ps3_background_folder = r'C:\games\Steam\steamapps\common\Umineko Chiru\bg'
mg_background_folder = r'C:\games\Steam\steamapps\common\Umineko Chiru\NSA_ext\bmp\background'

whitelist_paths = ['wsan_', 'wclo_', 'zf_', 'the_', 'different_']

def get_file_name_list(folder_to_scan):
    retval = []

    scanpath = os.path.join(folder_to_scan,'**')
    for path in glob.glob(scanpath, recursive=True):
        if '\\efe\\' in path:
            whitelisted = False
            for whitelist_path in whitelist_paths:
                if whitelist_path in path:
                    whitelisted = True

            if not whitelisted:
                continue

        if os.path.isfile(path):
            filename_with_ext = os.path.basename(path)
            name, ext = os.path.splitext(filename_with_ext)

            retval.append((name, os.path.relpath(get_with_file_extension(path, '.png'), folder_to_scan)))

            #
            # print(name, *splitName(name))

    return retval

mg_name_path = get_file_name_list(mg_background_folder)
ps3_name_path = get_file_name_list(ps3_background_folder)

class ImageInfo:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.name_start, self.name_modifiers = splitName(self.name)

    def __repr__(self):
        return f"{self.name} {self.name_start} {self.name_modifiers} {self.path}"

    # Calculate score in here?
    def compare(self, other : ImageInfo):
        match_score = 0
        if self.name_start == other.name_start:
            match_score += 10
            # print('name is the same')
            # print(mg_info.name, ps3_info.name)

        # this_len = len(self.name_modifiers)
        # other_len = len(other.name_modifiers)
        # for i in range(max(this_len, other_len)):
        #     if i >= this_len or i >= other_len:
        #         break
        #
        #     print(self.name_modifiers[i], other.name_modifiers[i])
        multiplier = 1
        for this_mod, other_mod in zip(self.name_modifiers, other.name_modifiers):
            # print(this_mod, other_mod)
            if this_mod == other_mod:
                match_score += multiplier
            multiplier /= 10

        return match_score

mg_infos = [ImageInfo(*x) for x in mg_name_path]
ps3_infos = [ImageInfo(*x) for x in ps3_name_path]

final_mapping = {}

for ps3_info in ps3_infos:
    mg_score_and_info = []

    for mg_info in mg_infos:
        match_score = ps3_info.compare(mg_info)
        mg_score_and_info.append((match_score, mg_info))
        # best_score = max(best_score, match_score)
        # if match_score > 10:
        #     print(mg_info.name, ps3_info.name, match_score, mg_info.name_modifiers, ps3_info.name_modifiers)


    mg_score_and_info.sort(reverse=True, key=lambda x: x[0])
    # print([x[0] for x in mg_score_and_info[0:3]])
    final_mapping[ps3_info] = mg_score_and_info[0]

with open('map_by_filename.txt', 'w') as outfile:
    for ps3_info,(score, mg_info)in final_mapping.items():
        if score < 10:
            print("failed to match", ps3_info.name)
            continue

        print(f"{ps3_info.name} -> {mg_info.name} {mg_info.path}")
        outfile.write(f"{ps3_info.name}|{mg_info.path}\n")