import os
import re
from typing import Tuple, List

tuple_regex = re.compile(r"""\('([^']*)', (\d+)""")

stralias_regex = re.compile(r"""stralias\s+([^,]+)\s*,\s*"([^"]+)""")
image_modifier_regex = re.compile(r':[^;]+;')

umineko_answer_script_input = r'C:\drojf\large_projects\umineko\umineko-answer\0.utf' #use to extract straliases

def get_with_file_extension(file_path : str, new_extension_with_dot : str):
    path_no_ext, ext = os.path.splitext(file_path)
    return path_no_ext + new_extension_with_dot


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

with open('simple_bg_mapping.txt', 'w') as simple_bg_mapping_file:
    for item in mangagamer_path_to_ps3_path:
        mangagamer_path = item[0]
        ps3_paths_to_copy_to = [x for x in item[1] if x not in ['black.png', 'white.png']]

        if mangagamer_path in ['black.png', 'white.png']:
            continue

        simple_bg_mapping_file.write(' '.join([mangagamer_path] + ps3_paths_to_copy_to) + '\n')

