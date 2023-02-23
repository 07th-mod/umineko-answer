from enum import Enum
import re

class VoicedelayLineInfo:
    def __init__(self, voice_on_line_to_insert, delay_to_insert, line_no):
        self.voice_on_line_to_insert = voice_on_line_to_insert
        self.delay_to_insert = delay_to_insert
        self.line_no = line_no
        self.inserted = False

def voicedelay_line_info(line):
    delay_on_line = None
    voice_on_line = None

    delay_match = re.search('(voicedelay\s+\d+)', line)
    if delay_match:
        delay_on_line = delay_match.group(1)
    else:
        raise Exception(f"Can't parse voicedelay on line {line}!")

    dwave_match = re.search('dwave_eng[^"]+"([^"]*)"', line)
    if dwave_match:
        voice_on_line = dwave_match.group(1)
    else:
        raise Exception(f"No dwave on voicedelay line {line}! Not an error in game script, but need to handle.")

    return (voice_on_line, delay_on_line)

script_path = '0.utf'
output_path = '0.fixed.utf'

with open(script_path, encoding='utf-8') as f:
    lines = f.readlines()


lines_to_insert : dict[str, VoicedelayLineInfo] = {}

# First pass - gather lines to insert
for line_no, line in enumerate(lines):
    if not line.startswith('*voicedelay') and not line.startswith('defsub') and 'voicedelay' in line:
        voice_on_line_to_insert, delay_to_insert = voicedelay_line_info(line)

        lines_to_insert[voice_on_line_to_insert.lower()] = VoicedelayLineInfo(voice_on_line_to_insert, delay_to_insert, line_no)
        print(f"{line.strip()} -> {delay_to_insert} | {voice_on_line_to_insert}")


# Second pass - apply fixes if line needs voicedelay insertion
with open(output_path, 'w', encoding='utf-8') as output:
    ordering_error = 0
    distance_error = 0

    for line_no, line in enumerate(lines):
        fixed_line = line

        dwave_match = re.search('dwave_jp[^"]+"([^"]*)"', line)
        if dwave_match:
            jp_voice = dwave_match.group(1)

            search_key = jp_voice.lower()

            if search_key in lines_to_insert:
                info = lines_to_insert[search_key]

                print(f"Need insert {info.delay_to_insert} onto line {line} ({info.line_no} -> {line_no})")

                # Do sanity checks before inserting
                if info.line_no - line_no < 0:
                    print(f"WARNING: ordering error on line {line_no}: {line} ")
                    ordering_error += 1
                elif info.line_no - line_no > 50:
                    print(f"WARNING: distance error on line {line_no}: {line} ")
                    distance_error += 1
                else:
                    fixed_line = line.replace("langjp:", f"langjp:{info.delay_to_insert}:")

                    # Sanity check that we actually inserted the voicedelay
                    if fixed_line == line:
                        raise Exception("Couldn't find place to insert voicedelay")

                    print(fixed_line)
                    info.inserted = True

        output.write(fixed_line)



not_inserted_count = 0
for key, value in lines_to_insert.items():
    if value.inserted != True:
        not_inserted_count += 1

print(f"ordering_error: {ordering_error} distance_error: {distance_error} not inserted: {not_inserted_count}")
