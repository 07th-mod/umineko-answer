import re
from typing import Dict


class SpriteModeLookup:
    def __init__(self):
        self.map = {} #type: Dict[str, int]

    def set_sprite_type(self, name: str, value: int):
        self.map[name] = int(value)

    def get_sprite_type(self, name: str) -> int:
        """
        The default type for a sprite is '1'
        :param name: sprite name, eg KUM
        :return: the number of the sprite
        """
        return self.map.get(name, 1)

    def reset_sprite_types(self):
        self.map.clear()


def getAddOrRemovedLineGroupsFromDiff(diffAllLines):
    """
    Returns a List[List[str]]
    :param diffAllLines: A List[str] - all the lines in the diff
    :return: Each inner list of contains some +lines (the old script ld) and some -lines (the new script ld)
    The returned list still has the '+' and '-' at the start of the line so you can differentiate which lines were added/removed
    """
    section_list = []
    current_section = None
    section_started = False

    for line in diffAllLines:
        if line[0] == '@':
            continue

        if line[0] not in [' ', '+', '-']:
            raise Exception("invalid line start character: ", line[0])

        if section_started:
            # a ' ' ends a section
            if line[0] == ' ':
                section_list.append(current_section)
                current_section = None
                section_started = False
            else:
                current_section.append(line)
        else:
            # a + or - starts a section
            if line[0] != ' ':
                section_started = True
                current_section = [line]

    if current_section is not None and len(current_section) > 0:
        section_list.append(current_section)

def getLineAndReplacementLines(diffLineGroups):
    """

    :param diffLineGroups: a list of line groups from getAddOrRemovedLineGroupsFromDiff
    :return:
    """

with open('sprite_diff.txt', 'r', encoding='utf-8') as sprite_diff_file:
    diffAllLines = sprite_diff_file.readlines()

with open(r'C:\drojf\large_projects\umineko\umineko-answer\0.utf', 'r', encoding='utf-8') as sprite_diff_file:
    currentScriptAllLines = sprite_diff_file.readlines()

change_clothes_simple = re.compile(r'^mov([^_]+)_Isyou')
change_clothes_command = re.compile(r'^mov\s+%([^_]+)_Isyou\s*,\s*(\d+)', re.IGNORECASE)


chapter_start = re.compile(r'^\*umi[5678]', re.IGNORECASE) #start of chapter or subchapter
teatime_start = re.compile(r'^\*teatime', re.IGNORECASE)
question_mark_teatime_start = re.compile(r'^\*ura', re.IGNORECASE)
eye_command = re.compile(r'^eye', re.IGNORECASE)

reset_regexes = [eye_command, chapter_start, teatime_start, question_mark_teatime_start]


# NOTES:
# Calling *DATA_SET resets sprites. Doesn't need to be checked as happens when you first start the game.#
# (*jump_sysdata_set1_1/2/3) should resets sprites (calls DATA_SET), but doesn't need to be checked because it is called each time you start a chapter (see below)

# - Chapter jump markers also seem to reset sprites, but might be unnecessary
# - Teatime should implicitly clear the sprites the because you restart the game?
# - Start of ??? should implicitly clear sprites because you restart the game
# - Calling the *eye functions reset sprites (calls DATA_SET)

# If the wrong sprite is classified, should be easy to tell unless it is 'never used'.
# As all? the outfits are used, should be pretty easy to identify these cases.

for line in diffAllLines:
    fullMatch = change_clothes_command.search(line[1:])
    if fullMatch:
        print(fullMatch.group(1), fullMatch.group(2), line)

    #check for irregular clothes change lines
    simpleMatch = change_clothes_simple.search(line[1:])
    if simpleMatch and not fullMatch:
        print("ERROR: irregular line", line)
        exit(-1)


    for reg in reset_regexes:
        resetMatch = reg.search(line[1:])
        if resetMatch:
            print(line)

    # if line[0] == '+' or line[0] == '-':
    #     if 'sprite' not in line and 'ld ' not in line:
    #         print(line)


import re

#
# class SpriteChunk:
#     PS3SpriteLineToSpritePathRegex = re.compile(r'(sprites\\[^"]+)', re.IGNORECASE)
#
#     def __init__(self, old_lines, new_lines, oldSpriteAliasDatabase):
#         """
#         Takes a list of old and new lines, without any '+' or '-'
#         :param old_lines:
#         :param new_lines:
#         """
#
#     def _get_old_sprite_name(self):
#
#     def _get_new_sprite_name(self):

# generate the mapping





# at this stage have something like this in each section
#['-_ld l,":b;sprites\\cla\\1\\cla_a11_akuwarai2.png",0\n', '-_ld r,":b;sprites\\nat\\1\\nat_a11_majime1.png",24\n', '-_ld l,":b;sprites\\cla\\1\\cla_a11_def1.png",80\n', '+ld l,KLA_akuwaraiA2,0\n', '+ld r,NAT_majimeA1,24\n', '+ld l,KLA_DefA1,80\n']

# print(f"Got {len(section_list)} items")
#
# sprite_chunks = []
#
# for section in section_list:
#     print('\n\nBEGIN SECTION')
#     old_sprites = []
#     new_sprites = []
#
#     for line in section:
#         if line[0] == '+':
#             old_sprites.append(line[1:])
#         elif line[0] == '-':
#             new_sprites.append(line[1:])
#         else:
#             raise Exception("invalid line start character")
#
#     # sprite_chunks.append(SpriteChunk(old_sprites, new_sprites))
#     sprite_chunks.append((old_sprites, new_sprites))
#     # print(old_sprites)
#     # print(new_sprites)
#
# #need to filter out bad lines from all_old like '\n' by itself!
# all_new = []
# for chunk in sprite_chunks:
#     all_new.extend(chunk[1])
#
#
# current_searched_line_index = 20
# for line in currentScriptAllLines:
#     if line == all_new[current_searched_line_index]:
#         current_searched_line_index += 1
#
# print(f"completed {current_searched_line_index} out of {len(all_new)}")
# print(f"Failed on {all_new[current_searched_line_index]}")