import re
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

with open('sprite_diff.txt', 'r', encoding='utf-8') as sprite_diff_file:
    diffAllLines = sprite_diff_file.readlines()

with open(r'C:\drojf\large_projects\umineko\umineko-answer\0.utf', 'r', encoding='utf-8') as sprite_diff_file:
    currentScriptAllLines = sprite_diff_file.readlines()

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
            chunks[-1].append(old_sprite_filepath)
            # if type != 1:
            #     print(f"Got old character alias:{old_character_name}_{old_character_emotion} type {type}")
        else:
            pass
            # print("failed on", line)
    elif line[0] == '-':
        ps3_match = PS3SpriteLineToSpritePathRegex.search(line)
        if ps3_match:
            ps3_sprite_path = ps3_match.group(1)
            chunks[-1].append(ps3_sprite_path)
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

for g in chunks:
    print(g)