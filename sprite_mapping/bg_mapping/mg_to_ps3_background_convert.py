import difflib
import glob
import os
import re
from collections import defaultdict

from lib import SpriteCounter
from util import get_with_file_extension
from typing import Tuple, List
import operator

# this path is only used to check manual override images actually exist (expect .png format images)
debug_check_mg_path = r'C:\temp\umiconv'
def check_mg_path_exists(path):
    return os.path.exists(os.path.join(debug_check_mg_path, path))

tuple_regex = re.compile(r"""\('([^']*)', (\d+)""")

stralias_regex = re.compile(r"""stralias\s+([^,]+)\s*,\s*"([^"]+)""")
image_modifier_regex = re.compile(r':[^;]+;')

umineko_answer_script_input = r'C:\drojf\large_projects\umineko\umineko-answer\0.utf' #use to extract straliases
only_used_images_folder = r'C:\temp\only_used_bg\bg'

map_by_filename_path  = r'..\map_by_filename\map_by_filename.txt'

# load in the mapping by filename
map_by_filename_mapping = {}
with open(map_by_filename_path, 'r') as inputFile:
    for line in inputFile:
        ps3_name, mg_path, score = line.strip().split('|')
        print(ps3_name)
        map_by_filename_mapping[ps3_name] = (mg_path, float(score))

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

def get_best_ps3_matches(mangagamer_path_to_ps3_path : List[Tuple[str, List[Tuple[str, int]]]]) -> List[Tuple[str, str]]:
    # get a list of all ps3 paths:
    all_ps3_paths = set()
    for mangagamer_path, ps3_path_score_tuples in mangagamer_path_to_ps3_path:
        for ps3_path, ps3_score in ps3_path_score_tuples:
            all_ps3_paths.add(ps3_path)

    # cha_p1by
    # for each ps3 path, accumulate which mg images match (with their scores)
    sc = SpriteCounter()
    for mangagamer_path, ps3_path_score_tuples in mangagamer_path_to_ps3_path:
        for ps3_path, ps3_score in ps3_path_score_tuples:
            sc.add_score(ps3_path, mangagamer_path, ps3_score)
            # all_ps3_paths_mapping[ps3_path][mangagamer_path]


    mapping = []
    for ps3_path in all_ps3_paths:
        mangagamer_paths_sorted = sc.get_value(ps3_path).most_common(1)
        score = mangagamer_paths_sorted[0][1]
        match_by_score = mangagamer_paths_sorted[0][0]

        final_match = match_by_score

        ps3_name, _ = os.path.splitext(ps3_path)
        maybe_mapping = map_by_filename_mapping.get(ps3_name.lower(), None)
        if maybe_mapping:
            match_by_filename, score_by_filename = maybe_mapping
            match_by_filename = os.path.join(r'BMP\background', match_by_filename)
            if score <= 2:
                if score_by_filename > .9:
                    print(f"Using filename mapping as too few statistical mappings: {ps3_name} was {match_by_score} now {match_by_filename}")
                    final_match = match_by_filename
        else:
            print("Maybe invalid ps3 path:", ps3_path, ps3_name)

        mapping.append((ps3_path, final_match))

    return mapping
    # construct the reverse mapping (mg copy to ps3) as expected by the next stage.
    # reverse_mapping = defaultdict(default_factory=list)
    # for ps3_path in all_ps3_paths:
    #     reverse_mapping.append((sc.get_value(ps3_path).most_common(1)[0][0],
    #                             [ps3_path]))
    #
    #
    # return reverse_mapping
    # for x in reverse_mapping:
    #     print(x)
    # retVal = []
    # for mangagamer_path, ps3_path_score_tuples in mangagamer_path_to_ps3_path:
    #     best_ps3_path, best_ps3_score = max(ps3_path_score_tuples, key=operator.itemgetter(1))
    #     #for legacy reasons, must return a list with one element here
    #     retVal.append((mangagamer_path, [best_ps3_path]))
    #
    # return retVal

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

        mangagamer_path_to_ps3_path.append((mangagamer_path, [(get_with_file_extension(x[0],'.png'), x[1]) for x in ps3_bg_name_tuples]))

best_ps3_to_mg_mapping = get_best_ps3_matches(mangagamer_path_to_ps3_path)
for x in best_ps3_to_mg_mapping:
    print(x)

########################################################################################################################

# Check if any ps3 backgrounds were never replaced
all_ps3_paths = set()
for ps3_path, _ in best_ps3_to_mg_mapping:
    all_ps3_paths.add(ps3_path)
# for mangagamer_path, ps3_paths in best_ps3_to_mg_mapping:
#     for ps3_path in ps3_paths:
#         all_ps3_paths.add(ps3_path.lower())


alternative_mg_to_ps3_paths = []

scanpath = os.path.join(only_used_images_folder,'**')
for used_ps3_path in glob.glob(scanpath, recursive=True):
    used_ps3_filename = os.path.basename(used_ps3_path)
    if used_ps3_filename.lower() not in all_ps3_paths:
        # print(f"{used_ps3_filename} was NOT covered!")
        used_ps3_name, _ = os.path.splitext(used_ps3_filename)
        alternate_mangagamer_mapping = map_by_filename_mapping.get(used_ps3_name.lower(), None)
        if alternate_mangagamer_mapping:
            print(f"Will use {used_ps3_name} -> {alternate_mangagamer_mapping[0]} alternate mapping")
            alternative_mg_to_ps3_paths.append((used_ps3_filename, os.path.join(r'bmp\background', alternate_mangagamer_mapping[0])))
        else:
            print(f"No mapping for {used_ps3_name}")

########################################################################################################################
# if the ps3 name exactly matches the mangagamer name, just use that file!
for i, (ps3_path, _) in enumerate(best_ps3_to_mg_mapping):
    ps3_name, _ = os.path.splitext(ps3_path)
    mangagamer_name_by_filename_tuple = map_by_filename_mapping.get(ps3_name.lower(), None)
    if mangagamer_name_by_filename_tuple:
        mangagamer_name_by_filename, score = mangagamer_name_by_filename_tuple
        if score >= 1.0:
            full_mg_path = os.path.join(r'bmp\background', mangagamer_name_by_filename)
            best_ps3_to_mg_mapping[i] = (ps3_path, full_mg_path)
            print(f"ps3 name {ps3_name} is identical, so using {best_ps3_to_mg_mapping[i]}")



########################################################################################################################

forced_overrides = {
'fea_r1ij.png': r'bmp\background\fea\fea_r1j.png',
'garden_1cp.png': r'bmp\background\garden\garden_1c.png',
'm_door3k.png': r'bmp\background\mainbuilding\m_door2.png',
'm_door5.png': r'bmp\background\mainbuilding\m_door1.png',  #this is an image of a door with tape with a bernkastel's name on it
'garden_1a.png' : r'bmp\background\garden\garden_1br.png',  #rain - building and roses
'garden_1ac.png' : r'bmp\background\garden\garden_1b.png',  #normal
'garden_1af.png' : r'bmp\background\garden\garden_1b.png',  #bright
'garden_1ar.png' : r'bmp\background\garden\garden_1bn.png',  #night
'garden_1c.png': r'bmp\background\garden\garden_1cr.png',  # rain - building and roses
'garden_1cc.png': r'bmp\background\garden\garden_1c.png',  # normal
'garden_1cf.png': r'bmp\background\garden\garden_1c.png',  # bright
'garden_1cn.png': r'bmp\background\garden\garden_1cn.png',  # night
'garden_r1a.png': r'bmp\background\garden\garden_r1ar.png',  # rain - building and roses
'garden_r1ac.png': r'bmp\background\garden\garden_r1a.png',  # normal
'garden_r1af.png': r'bmp\background\garden\garden_r1a.png',  # bright
'garden_r1an.png': r'bmp\background\garden\garden_r1an.png',  # night
'gdin_1ad.png': r'bmp\background\guesthouse\gdin_1b.png',
'gdin_1ad2.png': r'bmp\background\guesthouse\gdin_1c.png',
'm_o2a.png': r'bmp\background\mainbuilding\m_o1b.png',
'm_o2an.png': r'bmp\background\mainbuilding\m_o1bn.png',
'm_o2an_r.png': r'bmp\background\mainbuilding\m_o1br.png',
'm_o2ar.png': r'bmp\background\mainbuilding\m_o1br.png',
'm1f_r1a.png':r'bmp\background\guesthouse\g1f_r1a.png', #desk normal
'm1f_r1af.png':r'bmp\background\guesthouse\g1f_r1a.png', #desk bright
'm1f_r1am.png':r'bmp\background\guesthouse\g1f_r1an.png', #desk night
'm1f_r1ar.png':r'bmp\background\guesthouse\g1f_r1ar.png', #desk rain
'ros_p1a.png':r'bmp\background\rosehouse\ros_p1an.png',
'cha_i1ed.png': r'bmp\background\chapel\cha_i1j.png', #chapel stained glass window
'cha_i1ny.png': r'bmp\background\chapel\cha_i1n.png', #chapel pews
'm2f_r7a.png':r'bmp\background\mainbuilding\m2f_r1d.png',    #lamp
'm2f_r7ar.png':r'bmp\background\mainbuilding\m2f_r1dr.png',    #lamp
'cha_hisp.png': r'bmp\background\chapel\cha_i1j.png', #coffin in chapel, no purple effect
}

forced_ignore = [
'anm_no0019b.png',
'anm_no0020a.png',
'blue.png',
'cake_a.png',
'chain2r_sp.png',
# these are the doors at the end of the game. Can't remove them because it has the scrolling effect,
# and need to maintain consistency with that effect
'm_door4.png',
'm_door4_l.png',
'm_door4c.png',
'm_door4l.png',
'door_00096.png', #: r'bmp\background\garden\m_door4.png',
# end doors
# these are the portraits - they are identical in both versions of the game, but the ps3 ones are higher res
'portrait1.png',
'portrait2.png',
'portrait3.png',
#'portrait4.png', #this is never used in the Answer arcs I think
'portrait5.png',
'portrait6.png',
'red.png', #this is like a blood/cloud background image with a texture on it.
]

# Image which were replaced kind of properly but need fixing
#'fea_k3_green' - fea meta with eyes overlaid - mg has no eyes
#'fea_l4_green' - fea meta with eyes overlaid - mg has no eyes
#'goas_eye2c_cha'  # I think a custom image needs to be made for this one - it's eyes overlaid on the dark chapel 'cha'
#'goas_eye2c_cha2'
#'m_door1_nega' - negative colored door image...
#'hibun' - no matching mg image?
#'m_door2hp' - door with purple metaworld effect
#'mbat_1ap' - bath with purple metaworld effect
#'view_efe2_full' - These two images are peeking through door images. on their own their replacement is fine, but there
#'view_efe3_fill'   is an effect later on when you can see through a gap in the door, which only has a ps3 version currently.
#'mlib_1f' - image of window which rudolf breaks into
#'mlib_1f_r' - image of window which rudolf breaks into, with rudolf in the picture
#'moon_1p_1' - image of moon with siloute of rosa with gun
#'moon_1p_2' - image of moon with rosa with gun

forced_overrides_used = set()
for k,v in forced_overrides.items():
    forced_overrides_used.add(k)

forced_ignore_used = set(forced_ignore)

with open('simple_bg_mapping.txt', 'w') as simple_bg_mapping_file:
    for ps3_path, mangagamer_path in best_ps3_to_mg_mapping + alternative_mg_to_ps3_paths:
        if mangagamer_path in ['black.png', 'white.png'] or ps3_path in ['black.png', 'white.png']:
            continue

        override = forced_overrides.get(ps3_path, None)
        if override:
            print(f'Forced Override "{ps3_path}" old: {mangagamer_path} new: {override}')
            if not check_mg_path_exists(override):
                print(f"!!!!!! WARNING: override path {override} doesn't exist !!!!!!! ")
            mangagamer_path = override
            forced_overrides_used.remove(ps3_path)


        if ps3_path in forced_ignore:
            print(f"Manually ignored ps3 path {ps3_path}")
            forced_ignore_used.remove(ps3_path)
            continue

        simple_bg_mapping_file.write(f'{ps3_path}|{mangagamer_path}\n')

if len(forced_overrides_used) > 0:
    print("WARNING: the following forced overrides were not used:")
    print(forced_overrides_used)

if len(forced_ignore_used) > 0:
    print("WARNING: the following ignores were not used")
    print(forced_ignore_used)