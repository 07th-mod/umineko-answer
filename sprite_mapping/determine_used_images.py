import re

stralias_regex = re.compile(r"""stralias\s+([^\s,]+)[\s,]\s*"([^"]*)""")

umineko_answer_script_input = r'C:\drojf\large_projects\umineko\umineko-answer\0.utf' #use to extract straliases

with open(umineko_answer_script_input, 'r', encoding='utf-8') as umineko_answer_script_file:
    for line in umineko_answer_script_file.readlines():
        match = stralias_regex.search(line)
        if match:
            print(match.groups())
