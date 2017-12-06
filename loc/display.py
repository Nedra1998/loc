import os
import color

def print_lang(lang, width):
    return " {}\u25CF{} {:<{}} ".format(color.get_color(lang.color), color.get_color(color.Color.DEFAULT), lang.name, width)


def display_length(string):
    length = 0
    counting = 0
    for char in string:
        if char == '\033':
            counting = 1
        elif char == 'm' and counting == 1:
            counting = 0
            length -= 1
        if counting == 0:
            length += 1
    return length


def print_languages(items):
    rows, columns = os.popen("stty size", "r").read().split()
    rows = int(rows)
    columns = int(columns)
    lengths = [len(x.name) + 2 for x in items]
    count = len(lengths)
    col = 1
    while count / col > (rows * 0.25):
        col += 1
    while col * max(lengths) > columns:
        col -= 1
    width = max(lengths) - 2
    split = count / col
    groups = []
    last = 0.0
    while len(items) % int(split) != 0:
        items.append(None)
    split = len(items) / col
    while last < len(items):
        groups.append(items[int(last):int(last + split)])
        last += split
    for i in range(0, len(max(groups, key=len))):
        for li in groups:
            if len(li) > i and li[i] is not None:
                print(print_lang(li[i], width), end='')
            else:
                print(" " * (width + 3), end='')
        print('')
