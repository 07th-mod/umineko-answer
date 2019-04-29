import os
import shutil

whitelist_paths = ['wsan_', 'wclo_', 'zf_', 'the_', 'different_']

output_base_path = r'c:\temp\ps3_bg_output'
old_sprite_base_path = r'C:\temp\umiconv'

if os.path.exists('input'):
    output_base_path = 'ps3_output'
    old_sprite_base_path = 'input'

debug_expected_old_path = os.path.join(old_sprite_base_path, 'bmp')
if not os.path.exists(debug_expected_old_path):
    print(f"Can't find the 'bmp' folder containing the old backgrounds {debug_expected_old_path}. Please copy in the pachinko files to {debug_expected_old_path}.")
    exit(-1)

with open('simple_bg_mapping.txt', 'r') as simple_bg_mapping_file:
    for line in simple_bg_mapping_file.readlines():
        items = line.split()
        mg_path = items[0]
        ps3_path_list = items[1:]

        # full_ps3_filepath = os.path.join(output_base_path, ps3_filepath)
        full_mg_bg_path = os.path.join(old_sprite_base_path, mg_path)
        full_ps3_bg_paths = [os.path.join(output_base_path, x) for x in ps3_path_list]

        if '\\efe\\' in mg_path:
            whitelisted = False
            for whitelist_path in whitelist_paths:
                if whitelist_path in mg_path.lower():
                    whitelisted = True

            if not whitelisted:
                print("skipping efe file", mg_path)
                continue

        if not os.path.exists(full_mg_bg_path):
            print(f"Old sprite missing! {full_mg_bg_path}")
            continue

        print('will copy', full_mg_bg_path, 'to')
        for path in full_ps3_bg_paths:
            print(path)

        for full_ps3_path in full_ps3_bg_paths:
            os.makedirs(os.path.dirname(full_ps3_path), exist_ok=True)
            shutil.copy(full_mg_bg_path, full_ps3_path)
