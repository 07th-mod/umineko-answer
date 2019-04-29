from typing import List

############## PART 1 ANSWER #######################
def string_satisfies_pattern(s : str, pattern : str):
    return ''.join([x for x in filter(lambda x: x.isupper(), s)]) == pattern


def get_matching_words(l : List[str], pattern : str):
    return [x for x in l if string_satisfies_pattern(x, pattern)]

############## PART 2 ANSWER #######################
def string_satisfies_pattern_pt_2(s : str, pattern : str):
    i = 0

    for c in s:
        # early escape if pattern already matches
        if i >= len(pattern):
            return True

        if c == pattern[i]:
            i += 1

    return i >= len(pattern)

def get_matching_words_2(l : List[str], pattern : str):
    return [x for x in l if string_satisfies_pattern_pt_2(x, pattern)]


print('part 1')
matching_words = get_matching_words(["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"], 'FB')
print(matching_words)
print()

print('part 2')
matching_words = get_matching_words_2(["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"], 'FoBar')
print(matching_words)




#
#


#
# matching_words = get_matching_words(["FooBar","FooBarTest","FootBall","FrameBuffer","ForceFeedBack"], 'FB')
# print(matching_words)

# from typing import List
#
#
# def string_satisfies_pattern(s : str, pattern : str):
#     return ''.join(filter(lambda x: x.isupper(), s)) == pattern
#
#
# def get_matching_words(l : List[str], pattern : str):
#     return [x for x in l if string_satisfies_pattern(x, pattern)]
#
#
# print(matching_words)
#


