import os


def set_color(lang):
    color = lang.color.lstrip('#')
    if color == str():
        color = "939393"
    rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
    return "\033[38;2;{};{};{}m".format(rgb[0], rgb[1], rgb[2])


def print_lang(lang, width):
    return "{}\u25CF\033[0m {:<{}} ".format(set_color(lang), lang.name, width)


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
    #  print(col)
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
