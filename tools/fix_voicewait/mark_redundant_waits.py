from typing import List
import re

class Lexeme:
	def __init__(self, type, text):
		self.text = text
		self.type = type

	def __repr__(self):
		return f"{self.type}: {self.text}"


def getTrueStringLength(s):
	s = s.replace('^', '').replace('!sd', '')
	s = re.sub('!d\d+', '', s)
	s = re.sub('!s\d+', '', s)
	s = re.sub('!w\d+', '', s)

	return len(s)


def dialogueStartsWithDelay(s):
	return re.match('!d\d+', s) is not None


class Processor:

	def __init__(self):
		self.all_final_tokens = set()
		self.got_dwave = False
		self.lines_need_voicedelay = []

	def process_map_line(self, i: int,  line: str, map_line: List[Lexeme]):
		# Skip lines at end of script
		# if i > 301550:
		# 	return None

		# map_line = [l for l in map_line_unfiltered if l.type not in ['COMMENT', 'HEX_COLOR']]
		#
		if len(map_line) == 0 or map_line[0].text == 'langjp':
			return None
		#
		# if map_line[0].text == 'langen':
		# 	final_token = map_line[-1]
		# 	if final_token.type not in self.all_final_tokens:
		# 		print(f'[{i}]: {final_token}')
		# 	self.all_final_tokens.add(final_token.type)

		for lexeme in map_line:
			if lexeme.type == 'WORD' and lexeme.text == 'dwave_eng':
				if self.got_dwave == False:
					self.got_dwave = True
				else:
					print(f"Detected missing delay at [{i+1}]: {line}")
					self.lines_need_voicedelay.append(i)
			elif lexeme.type == 'AT_SYMBOL' or lexeme.type == 'BACK_SLASH':
				self.got_dwave = False
			elif lexeme.type == 'WORD' and lexeme.text == 'delay':
				self.got_dwave = False
			elif lexeme.type == 'DIALOGUE' and dialogueStartsWithDelay(lexeme.text):
				self.got_dwave = False


		# for lexeme in map_line:
		# 	print(lexeme)
			# if lexeme.type == 'WORD' and lexeme.text == 'sl':
			# 	self.sl_waiting_for_langen = True
			# 	self.sl_waiting_for_langen_line_no = i
			# elif lexeme.type == 'WORD' and lexeme.text == 'langen':
			# 	self.sl_waiting_for_langen = False
			# 	if self.sl_needs_replacement is not None:
			# 		self.sl_needs_move_down_lines.append(f'{self.sl_needs_replacement}>{i}')
			#
			# 	self.sl_needs_replacement = None
			# elif lexeme.type == 'WORD' and lexeme.text == 'langjp':
			# 	pass
			# elif self.sl_waiting_for_langen:
			# 	print(f"Warning: sl at {self.sl_waiting_for_langen_line_no + 1} is in the wrong location, should be moved down")
			# 	self.sl_waiting_for_langen = False
			# 	self.sl_needs_replacement = self.sl_waiting_for_langen_line_no
			#
			# if lexeme.type == 'WORD' and lexeme.text == 'sl':
			# 	self.handle_cumulative_text(i, line, current_is_sl=True)
			# 	self.last_was_sl = True
			# 	self.last_sl_index = i
			# elif lexeme.type == 'AT_SYMBOL' or lexeme.type == 'BACK_SLASH':
			# 	self.handle_cumulative_text(i, line, current_is_sl=False)
			# 	self.last_was_sl = False
			# elif lexeme.type == 'DIALOGUE':
			# 	self.cumulative_text.append(lexeme.text)

		# TODO: if found excessively short line, print it out.



if __name__ == '__main__':
	with open("decoded.txt", 'r', encoding='utf-8') as map:
		map_temp = map.readlines()

	map_lines = []
	for line in map_temp:
		pairs = []
		parts = line.split("\x00")
		for i in range(len(parts)//2):
			pairs.append(Lexeme(parts[2*i], parts[2*i+1]))

		map_lines.append(pairs)

	p = Processor()

	for i in range(len(map_lines)):
		p.process_map_line(i, map_temp[i], map_lines[i])

	print(p.all_final_tokens)

	#
	# with open("zero_lines.txt", 'w', encoding='utf-8') as f:
	# 	f.writelines(str(i) + '\n' for i in p.zero_lines)
	#
	# with open("short_lines.txt", 'w', encoding='utf-8') as f:
	# 	f.writelines(str(i) + '\n' for i in p.short_lines)
	#
	with open("lines_need_voicedelay.txt", 'w', encoding='utf-8') as f:
		f.writelines(str(i) + '\n' for i in p.lines_need_voicedelay)
