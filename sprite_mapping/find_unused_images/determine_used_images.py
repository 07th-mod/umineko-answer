import re

start_marker = 'seventh_change_voice_level 0 ;initialize voice volume'

stralias_regex = re.compile(r"""stralias\s+([^\s,]+)[\s,]\s*"([^"]*)""")

umineko_answer_script_input = r'C:\drojf\large_projects\umineko\umineko-answer\0.utf' #use to extract straliases

mapping_lowercase = {}

with open(umineko_answer_script_input, 'r', encoding='utf-8') as umineko_answer_script_file:
    all_lines = umineko_answer_script_file.readlines()

# split script into the header/start section
split_line_number = None
for i, line in enumerate(all_lines):
    if start_marker in line:
        split_line_number = i
        break

definition_lines = all_lines[:split_line_number]
game_lines = all_lines[split_line_number:]

for line in definition_lines:
    match = stralias_regex.search(line)
    if match:
        alias_name = match.group(1)
        path = match.group(2)
        if 'bmp\\background' in path.lower():
            print('Skipping as is old background:', path)
            continue

        if alias_name.lower() in mapping_lowercase:
            # I think the game engine doesn't care about case
            if mapping_lowercase[alias_name.lower()].lower() == path.lower():
                print("Warning, alias already exists (but was the same)!", alias_name, path, mapping_lowercase[alias_name.lower()])
            else:
                print("Warning, alias already exists (but is different)!", alias_name, path, mapping_lowercase[alias_name.lower()])
        else:
            mapping_lowercase[alias_name.lower()] = path


with open('umineko_answer_used_bgs.txt', 'w') as used_bgs_file:
    for k,v in mapping_lowercase.items():
        found = False
        for line in game_lines:
            if k.lower() in line.lower():
                found = True

        was_used_string = f'{k}|{"WAS_FOUND" if found else "NEVER_USED"}|{v}\n'
        print(was_used_string)
        used_bgs_file.write(was_used_string)