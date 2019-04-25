import csv
import pickle
import re
from typing import List, Tuple

from lib import *

change_clothes_simple = re.compile(r'^mov([^_]+)_Isyou')
change_clothes_command = re.compile(r'^mov\s+%([^_]+)_Isyou\s*,\s*(\d+)', re.IGNORECASE)

chapter_start = re.compile(r'^\*umi[5678]', re.IGNORECASE) #start of chapter or subchapter
teatime_start = re.compile(r'^\*teatime', re.IGNORECASE)
question_mark_teatime_start = re.compile(r'^\*ura', re.IGNORECASE)
eye_command = re.compile(r'^eye', re.IGNORECASE)
reset_regexes = [eye_command, chapter_start, teatime_start, question_mark_teatime_start]

character_alias = re.compile(r'(\w{3})_(\w+)[^\w.]', re.IGNORECASE)
PS3SpriteLineToSpritePathRegex = re.compile(r'(sprites\\[^"]+)', re.IGNORECASE)


def generate_chunks():
    with open('sprite_diff.txt', 'r', encoding='utf-8') as sprite_diff_file:
        diffAllLines = sprite_diff_file.readlines()

    # with open(r'C:\drojf\large_projects\umineko\umineko-answer\0.utf', 'r', encoding='utf-8') as sprite_diff_file:
    #     currentScriptAllLines = sprite_diff_file.readlines()

    sprite_clothes_lookup = SpriteModeLookup()

    chunks = [[]]

    # The first five lines are assumed to have the diff header, so skip them.
    for line in diffAllLines[5:]:
        # search for a clothes change command
        m = change_clothes_command.search(line[1:])
        if m:
            character_name = m.group(1)
            clothes_number = int(m.group(2))
            # print(character_name, clothes_number, line)
            sprite_clothes_lookup.set_sprite_type(character_name, clothes_number)
        elif change_clothes_simple.search(line[1:]):
            # double check that a change clothes command has not been missed
            # by using a simpler regex which should match on more or less the same thing
            print("ERROR: irregular line", line)
            exit(-1)

        # check for a clothes reset command
        for reg in reset_regexes:
            resetMatch = reg.search(line[1:])
            if resetMatch:
                # print(line)
                sprite_clothes_lookup.reset_sprite_types()

        # TODO: chunking should take into account lines with spaces only - in that case should treat as the same chunk.
        # There seem to be enough matches so it turns out OK, except for rarely used sprites.
        # '+' -> check for a old character sprite alias
        # '-' -> check for ps3 sprite path
        # ' ' -> start a new chunk of '+' and '-' type lines
        if line[0] == '+':
            # print(line)
            characterMatch = character_alias.search(line)
            if characterMatch:
                old_character_name = characterMatch.group(1)
                old_character_emotion = characterMatch.group(2)
                variant = sprite_clothes_lookup.get_sprite_type(old_character_name)
                old_sprite_filepath = get_old_sprite_path(old_character_name, old_character_emotion, variant)
                chunks[-1].append(old_sprite_filepath.lower())
                # if type != 1:
                #     print(f"Got old character alias:{old_character_name}_{old_character_emotion} type {type}")
            else:
                pass
                # print("failed on", line)
        elif line[0] == '-':
            ps3_match = PS3SpriteLineToSpritePathRegex.search(line)
            if ps3_match:
                ps3_sprite_path = ps3_match.group(1)
                chunks[-1].append(ps3_sprite_path.lower())
            else:
                pass
                # print("failed on", line)
        elif line[0] == ' ':
            if chunks[-1]:
                chunks.append([])
        else:
            raise Exception("unknown line type", line)

    # if the last element of the array is an empty list, remove it
    if not chunks[-1]:
        chunks.pop()

    return chunks


def convert_frequency_list_to_percentage(l : List[Tuple[str, int]]):
    total = sum([x[1] for x in l])
    return [(x[0], x[1]/total * 100) for x in l]


# this function should also return match percentage/count?
# Rules:
# - If there is only one matched value, use that value
# - If the percentage is greater than 80%, use the first (>80%) value
# - If a result has identical emotion in name, use that
# - Otherwise, don't match and let user match manually
def get_best_match(ps3_sprite_path : str, old_sprites_sorted : List[Tuple[str, int]]):
    percent_list = convert_frequency_list_to_percentage(old_sprites_sorted)

    # TODO: don't match if there is only one match in the list, as the uncertainty is high - do some other method of matching
    # Currently check for at least 2 matches if there is only one type of sprite matched
    if len(percent_list) == 1 and old_sprites_sorted[0][1] > 1:
        return percent_list[0]
    elif percent_list[0][1] > 80:
        return percent_list[0]
    else:
        ps3_sprite_path_no_ext = ps3_sprite_path.replace(".png", '')
        ps3_expression = ps3_sprite_path_no_ext.split('_')[-1]

        old_expressions = [value[0].split('_')[-1] for value in old_sprites_sorted]
        old_expressions_noletter = [x[:-2] + x[-1] for x in old_expressions]

        for i in range(0, len(old_expressions_noletter)):
            if old_expressions_noletter[i] == ps3_expression:
                matched_val = percent_list[i]
                print(f"Matched {ps3_sprite_path} to {matched_val} by name")
                return matched_val

        return ("<NO MATCH!!>", percent_list[0][1])

regenerate_input = input("Regenerate Input (yes/no, default=no)")

if regenerate_input and regenerate_input[0] == 'y':
    with open('data.pickle', 'wb') as f:
        chunks = generate_chunks()
        pickle.dump(chunks, f, pickle.HIGHEST_PROTOCOL)

with open('data.pickle', 'rb') as f:
    chunks = pickle.load(f)


# Create a data structure to measure the amount of times
sprite_counter = SpriteCounter()

# for now, just ignore any 'unmatchable' values
for g in chunks:
    if len(g) % 2 != 0:
        #print(g)
        continue

    old_paths = g[len(g)//2:]
    ps3_paths = g[:len(g)//2]

    for (ps3, old) in zip(ps3_paths, old_paths):
        sprite_counter.add_value(ps3, old)

# generate the output map
output_rows = []
for k, v in sprite_counter.map.items():
    corresponding_old_sprites = v.most_common()
    best_match, percent = get_best_match(k, corresponding_old_sprites)
    print(k, best_match)
    output_rows.append([k, best_match, percent] + [str(x) for x in corresponding_old_sprites])

# First should just print out all matches in csv format
# then make a function which 'chooses' the correct match from the list of matches
# and does something else if undecided
with open('mapping.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['ps3', 'best_match', 'percent', 'all_matches'])
    for row in reversed(sorted(output_rows, key=lambda x: x[2])):
        writer.writerow(row)
