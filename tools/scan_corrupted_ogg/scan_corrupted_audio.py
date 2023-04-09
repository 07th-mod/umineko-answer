import os
import re
import subprocess
from pathlib import Path
from progress.bar import Bar
import statistics

def get_db_arg(arg_name, ffmpeg_output):
    match = re.search(f'{arg_name}:\s*([^ ]*)', ffmpeg_output)
    return match.groups()[0]

def generate_database(search_folder, total_files, database_path, quit_early=False):
    search_path = Path(search_folder)

    with open(database_path, 'w', encoding='utf-8') as f:
        f.write(f'path mean max\n')
        for cnt, ogg_path in Bar('Processing', max=total_files).iter(enumerate(search_path.rglob('*.ogg'))):
            rel_path = ogg_path.relative_to(search_path)
            # print(ogg_path)

            cmd = ['ffmpeg', '-accurate_seek', '-sseof', '-5ms', '-i', ogg_path, '-filter:a', 'volumedetect', '-f', 'null', '/dev/null']

            # FFMPEG outputs its text/progress output to stderr!
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)

            # print('output size', len(output))

            mean_volume = float(get_db_arg('mean_volume', output))
            max_volume = float(get_db_arg('max_volume', output))
            f.write(f'{rel_path} {mean_volume} {max_volume}\n')

            # if mean_volume > -6:
            #     print(f"Found corrupted ogg file {ogg_path} mean: {mean_volume} max: {max_volume}")
            #     f.write(f'{ogg_path} {mean_volume} {max_volume}\n')

            # print(f'Mean Volume: {mean_volume} Max Volume: {max_volume}')

            if quit_early and cnt > 10:
                break

class Entry:
    def __init__(self, path, mean, max):
        self.path = path
        self.mean = mean
        self.max = max

# search_folder = 'C:/temp/New folder (71)/voice'
database_path = 'stats.txt'
search_folder = 'W:/SteamLibrary/steamapps/common/Umineko Chiru Modded/voice_old'
at3_folder = 'W:/07th-mod/Umineko ISO files/Answer/voice'
fixed_folder = 'fixed_ogg'
total_files = 46_968

# Generate the database only if it doesn't already exist
if not os.path.exists(database_path):
    generate_database(search_folder, total_files, database_path + '.temp')
    os.rename(database_path + '.temp', database_path)


entries = []

with open(database_path, encoding='utf-8') as f:
    first_line = True
    for line in f.readlines():
        if first_line:
            first_line = False
            continue

        # print(line.split())
        path, mean, max = line.split()
        entries.append(Entry(path, float(mean), float(max)))

mean_loudness_mean = statistics.mean([x.mean for x in entries])
mean_loudness_max = statistics.mean([x.max for x in entries])


print(f"Got {len(entries)} lines")
print(f"Mean loudness mean: {mean_loudness_mean}")
print(f"Mean loudness max: {mean_loudness_max}")

corrupted_file_list = []

cnt = 0
with open('corrupted_ogg2.txt', 'w', encoding='utf-8') as f:
    for entry in entries:
        if entry.mean > -6 or entry.max > -3:
            corrupted_file_list.append(entry.path)
            f.write(f"{entry.path} {entry.mean} {entry.max}\n")
            cnt += 1

print(f"Found {cnt} corrupted files")


for corrupted_file in corrupted_file_list:
    stem_folder = Path(Path(corrupted_file).with_suffix(''))
    src = Path(at3_folder).joinpath(stem_folder.with_suffix('.at3'))
    temp = Path(fixed_folder).joinpath(stem_folder.with_suffix('.wav'))

    os.makedirs(Path(temp).parent, exist_ok=True)

    # The length will be incorrect for certain .at3 files if converting directly to .ogg
    # To get around this, convert to .wav first, then conver the .wav to .ogg
    print(f"Will convert {src} -> {temp}")
    subprocess.check_call(['ffmpeg', '-y', '-i', src, '-ar', '44100', '-ac', '1', temp])

    dst = Path(temp).with_suffix('.ogg')

    subprocess.check_call(['ffmpeg', '-y', '-i', temp, '-ar', '44100', '-ac', '1', '-q', '8', dst])

    os.remove(temp)
