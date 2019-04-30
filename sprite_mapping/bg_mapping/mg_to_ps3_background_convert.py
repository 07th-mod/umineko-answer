import glob
import os
import re
from util import get_with_file_extension
from typing import Tuple, List

tuple_regex = re.compile(r"""\('([^']*)', (\d+)""")

stralias_regex = re.compile(r"""stralias\s+([^,]+)\s*,\s*"([^"]+)""")
image_modifier_regex = re.compile(r':[^;]+;')

umineko_answer_script_input = r'C:\drojf\large_projects\umineko\umineko-answer\0.utf' #use to extract straliases
only_used_images_folder = r'C:\temp\only_used_bg\bg'

map_by_filename_path  = r'..\map_by_filename\map_by_filename.txt'

def deserialize_tuple_list(s : str) -> List[Tuple[str, int]]:
    stripped = s.strip().strip('[]')
    return [(m.group(1), int(m.group(2))) for m in tuple_regex.finditer(stripped)]

def get_aliases():
    """
    :return: alias to path mapping, where the alias name is always all lowercase, and the path always has a .png extension
    """
    aliases = {}
    with open(umineko_answer_script_input, 'r', encoding='utf-8') as umineko_answer_script_file:
        for line in umineko_answer_script_file.readlines():
            match = stralias_regex.search(line)
            if match:
                alias_name = match.group(1)
                path_with_modifier = match.group(2)
                path = image_modifier_regex.sub('', path_with_modifier)
                aliases[alias_name.lower()] = get_with_file_extension(path, '.png')

    return aliases

mangagamer_path_to_ps3_path = []

mangagamer_alias_to_path = get_aliases()

with open('bg_match_statistics.txt', 'r', encoding='utf-8') as statistics_file:
    for line in statistics_file.readlines():
        if '-----------Result ---------------' in line:
            continue
        if 'Total Items Printed:  1085' in line:
            continue

        mangagamer_alias, ps3_bg_name_tuples_str = line.split(' maps to ')
        ps3_bg_name_tuples = deserialize_tuple_list(ps3_bg_name_tuples_str)

        # mapping[mangagamer_bg_name] = [x[0] for x in ps3_bg_name_tuples]
        mangagamer_path = mangagamer_alias_to_path.get(mangagamer_alias.lower(), None)
        if mangagamer_path is None:
            print(f"WARNING: couldn't find alias for {mangagamer_alias} - skipping")
            continue

        mangagamer_path_to_ps3_path.append((mangagamer_path, [get_with_file_extension(x[0],'.png') for x in ps3_bg_name_tuples]))

# Check if any ps3 backgrounds were never replaced
all_ps3_paths = set()
for mangagamer_path, ps3_paths in mangagamer_path_to_ps3_path:
    for ps3_path in ps3_paths:
        all_ps3_paths.add(ps3_path.lower())

# load in the mapping by filename
map_by_filename_mapping = {}
with open(map_by_filename_path, 'r') as inputFile:
    for line in inputFile:
        ps3_name, mg_path = line.strip().split('|')
        print(ps3_name)
        map_by_filename_mapping[ps3_name] = mg_path

alternative_mg_to_ps3_paths = []

scanpath = os.path.join(only_used_images_folder,'**')
for used_ps3_path in glob.glob(scanpath, recursive=True):
    used_ps3_filename = os.path.basename(used_ps3_path)
    if used_ps3_filename.lower() not in all_ps3_paths:
        # print(f"{used_ps3_filename} was NOT covered!")
        used_ps3_name, _ = os.path.splitext(used_ps3_filename)
        alternate_mangagamer_mapping = map_by_filename_mapping.get(used_ps3_name.lower(), None)
        if alternate_mangagamer_mapping:
            print(f"Will use {used_ps3_name} -> {alternate_mangagamer_mapping} alternate mapping")
            alternative_mg_to_ps3_paths.append((os.path.join(r'bmp\background', alternate_mangagamer_mapping), [used_ps3_filename]))
        else:
            print(f"No mapping for {used_ps3_name}")

with open('simple_bg_mapping.txt', 'w') as simple_bg_mapping_file:
    for mangagamer_path, ps3_paths in mangagamer_path_to_ps3_path + alternative_mg_to_ps3_paths:
        ps3_paths_to_copy_to = [x for x in ps3_paths if x not in ['black.png', 'white.png']]

        if mangagamer_path in ['black.png', 'white.png']:
            continue

        simple_bg_mapping_file.write(' '.join([mangagamer_path] + ps3_paths_to_copy_to) + '\n')

