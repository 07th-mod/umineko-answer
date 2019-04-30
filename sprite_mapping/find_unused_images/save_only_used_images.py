import os
import shutil

used_images_list = 'umineko_answer_used_bgs.txt'

source_folder = r'C:\games\Steam\steamapps\common\Umineko Chiru'
dest_folder = r'c:\temp\only_used_bg'

with open(used_images_list, 'r') as used_images_file:
    for line in used_images_file:
        alias, used_string, path_with_modifier = line.strip().split('|')

        if used_string == 'NEVER_USED':
            used = False
        elif used_string == 'WAS_FOUND':
            used = True
        else:
            raise Exception("invalid used marker in used_bgs listing")


        modifier, path = path_with_modifier.split(';')

        full_source_path = os.path.join(source_folder, path)
        full_dest_path = os.path.join(dest_folder, path)
        if not os.path.exists(full_source_path):
            print(f"Warning: {full_source_path} doesn't exist!")
            exit(-1)

        if used:
            os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)
            shutil.copy(full_source_path, full_dest_path)

