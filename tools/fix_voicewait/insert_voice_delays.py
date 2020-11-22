import os
import pickle
import re

lines_need_insertion = set()


get_voice_regex = re.compile(r'dwave_eng\s+\d+\s*,\s*"([^"]+)"', flags=re.IGNORECASE)

# there are two types of voiced lines - ones which use alias and ones which are hardcoded.
# def try_get_voice_on_line(line, show_output = True):
#	 all_voices = re.findall(get_voice_regex, line)
#
#	 if all_voices:
#		 raise Exception("a mix of ogg files and raw paths on same line! this case is not handled properly", line)
#
#	 if len(all_voices) > 0:
#		 if show_output:
#			 print('got voice alias: ',  all_voices[-1])
#		 return all_voices[-1]
#
#	 raise Exception("couldn't find voice file in line '{}'".format(line.strip()))

def convertVoiceSecondsToScriptDelay(voiceLength):
	return int(round(voiceLength, 2)*1000)

def get_audio_length_as_script_delay(filepath, voice_file_length_dict):
	normalized_path = os.path.normpath(filepath)
	# print(filepath, normalized_path)

	return convertVoiceSecondsToScriptDelay(voice_file_length_dict[normalized_path])

with open('voice_length_database_answer.pickle', 'rb') as f:
	voice_file_length_dict = pickle.load(f)

with open("lines_need_voicedelay.txt", 'r', encoding='utf-8') as f:
	for line in f:
		lines_need_insertion.add(int(line))

with open("../../0.utf", 'r', encoding='utf-8') as file:
	all_lines = file.readlines()

output = []

# total_redundant_sl = 0
last_voice_file = None
for i in range(len(all_lines)):
	line = all_lines[i]

	if i in lines_need_insertion:
		print("Getting audio length for", last_voice_file)
		delay_length_ms = get_audio_length_as_script_delay(last_voice_file, voice_file_length_dict)
		(new_line, num_subs) = re.subn('langen:', f'langen:delay {delay_length_ms}:', line)
		if num_subs != 1:
			raise Exception(f"Missing or dup langen: at line {i + 1}: {line}")

		output.append(new_line)
		last_voice_file = None
	else:
		output.append(line)

	# get the last voice file on the current line
	if re.match('\s*langen', line):
		if 'dwave_eng' in line:
			all_voices_on_line = []

			for match in get_voice_regex.finditer(line):
				all_voices_on_line.append(match.group(1))

			if len(all_voices_on_line) == 0:
				raise Exception(f"Failed to parse voice files at {i + 1}: {line}")

			last_voice_file = all_voices_on_line[-1].lower()


with open("lines_with_voice_delay.u", 'w', encoding='utf-8') as f:
	f.writelines(output)
