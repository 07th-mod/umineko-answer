import csv
import os
import shutil

output_base_path = r'c:\temp\ps3_output'
old_sprite_base_path = r'C:\games\Steam\steamapps\common\Umineko Chiru\NSA_ext\big'

if os.path.exists('big'):
    output_base_path = 'ps3_output'
    old_sprite_base_path = 'big'

debug_expected_old_path = os.path.join(old_sprite_base_path, 'bmp\\tati')
if not os.path.exists(debug_expected_old_path):
    print(f"Can't find the 'tati' folder containing the old pachinko sprites in {debug_expected_old_path}. Please copy in the pachinko files to {debug_expected_old_path}.")
    exit(-1)

# TODO: look for duplicate entries
with open('mapping_custom.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)

    for i, row in enumerate(reader):
        if i == 0:
            continue

        ps3_filepath = row[0] #already has .png
        old_filepath = row[1] + '.png'

        if 'NO MATCH' in old_filepath:
            print("Skipping row as no match: ", row)
            continue

        invalid = False
        if 'sprites' in old_filepath:
            print(f"invalid old filepath {old_filepath}")
            invalid = True

        if 'bmp' in ps3_filepath:
            print(f"invalid ps3 filepath {ps3_filepath}")
            invalid = True

        if invalid:
            continue

        full_ps3_filepath = os.path.join(output_base_path, ps3_filepath)
        full_old_sprite_filepath = os.path.join(old_sprite_base_path, old_filepath)

        if not os.path.exists(full_old_sprite_filepath):
            print(f"Old sprite missing! {full_old_sprite_filepath} (from {full_ps3_filepath})")
            continue

        # print(f'copying {ps3_filepath} -> {old_filepath}')
        os.makedirs(os.path.dirname(full_ps3_filepath), exist_ok=True)
        shutil.copy(full_old_sprite_filepath, full_ps3_filepath)



# zoom folder is handled separately! images should have the same file names, so should be easy.