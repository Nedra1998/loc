#!/usr/bin/python3

import os
from operator import add
from os import listdir
from os.path import isfile, join
import yaml
import json
import pprint
import argparse
import display
import table
import color


class Language(object):

    def __init__(self, name=str(), ext=list(), com=list(), type="(null)", color="#000000", id=0):
        self.name = name
        self.extensions = ext
        self.comments = com
        self.id = id
        self.color = color
        self.type = type

    def __repr__(self):
        return "{}".format(self.name)
        #  return "<[{}]{}: {}, {}, {}>".format(self.id, self.name, self.extensions, self.comments, self.color)


languages = list()
#  languages.append(Language("Bash", ["bash"], ["#"]))
#  languages.append(
    #  Language("C++", ["cpp", "cxx", "c++", "hpp", "hxx", "h++"], ["//"]))
#  languages.append(Language("C", ["c", "h"], ["//"]))
#  languages.append(Language("Python", ["py"], ["#", "\"\"\""]))


def print_table(table, has_title=False, colors=list(), col=None):
    if col is not None:
        lengths = [0] * col
    else:
        lengths = [0] * len(table[0])
    while len(colors) < len(lengths):
        colors.append("")
    for i, color in enumerate(colors):
        if type(color) is int:
            colors[i] = "\033[{}m".format(color)
    for row in table:
        for i in range(0, len(lengths)):
            if type(row[i]) is not str:
                lengths[i] = max(len(str(row[i]) + 2, lengths[i]))
            else:
                lengths[i] = max(len(row[i]) + 2, lengths[i])
    if has_title is True:
        titles = table[0]
        table = table[1:]
        print("\u250f", end="")
        for length in lengths[:-1]:
            print("\u2501" * length, end='')
            print("\u2533", end='')
        print("\u2501" * lengths[-1], end='')
        print("\u2513")
        print("\u2503", end='')
        for i, ent in enumerate(titles):
            print(" {:{width}}".format(ent, width=lengths[i] - 1), end='')
            print("\u2503", end='')
        print("")
        print("\u2521", end='')
        for length in lengths[:-1]:
            print("\u2501" * length, end='')
            print("\u2547", end='')
        print("\u2501" * lengths[-1], end='')
        print("\u2529")

    else:
        print("\u250c", end='')
        for length in lengths[:-1]:
            print("\u2500" * length, end='')
            print("\u252c", end='')
        print("\u2500" * lengths[-1], end='')
        print("\u2510")
    for entry in table:
        print("\u2502", end='')
        for i in range(0, len(lengths)):
            print(
                "{} {:{width}}\033[0m".format(
                    colors[i], entry[i], width=lengths[i] - 1),
                end='')
            print("\u2502", end='')
        print("")
    print("\u2514", end='')
    for length in lengths[:-1]:
        print("\u2500" * length, end='')
        print("\u2534", end='')
    print("\u2500" * lengths[-1], end='')
    print("\u2518")


def load_languages():
    global languages
    data = json.load(open("languages.json"))
    for key, value in data.items():
        lang = Language(key, value['extensions'], value['comments'], value['type'], value['color'], value['id'])
        languages.append(lang)

def save_languages():
    global languages
    data = dict()
    for lang in languages:
        data[lang.name] = {"type": lang.type, "color": lang.color, "extensions": lang.extensions , "comments": lang.comments, "id": lang.id}
    with open("languages.json", "w") as out:
        json.dump(data, out)


def lang_from_ext(ext):
    global languages
    for lang in languages:
        #  print(ext, lang.extensions)
        if ext in lang.extensions:
            #  print(ext, "is in")
            return lang
    return None


def is_binary(path):
    if path is None:
        return None
    try:
        if not os.path.exists(path):
            return
    except Exception:
        return
    fin = open(path, 'rb')
    try:
        CHUNKSIZE = 1024
        while True:
            chunk = fin.read(CHUNKSIZE)
            if b'\0' in chunk:  # found null byte
                return True
            if len(chunk) < CHUNKSIZE:
                break  # done
        return False
    finally:
        fin.close()


def lang_from_shebang(file):
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    shebang_line = str()
    if is_binary_string(open(file, "rb").read(1024)):
        return None
    #  print(file)
    with open(file) as f:
        shebang_line = f.readline()
        f.close()
    if shebang_line and shebang_line.find("#!") == 0:
        shebang_line = shebang_line.replace("#!", "", 1)
        shebang_line = shebang_line.strip()
    else:
        return
    shebang_line = shebang_line.split('/')[-1].lower()
    global languages
    for lang in languages:
        if shebang_line == lang.name.lower():
            return lang
    return None


def find_language(file_path):
    name, ext = os.path.splitext(file_path)
    if ext != str():
        return lang_from_ext(ext)
    else:
        return lang_from_shebang(file_path)


def count_file(file_path):
    language = find_language(file_path)
    if language is None:
        return None
    #  print(language)
    data = [[0, 0, 0], [0, 0, 0]]
    with open(file_path) as raw:
        for line in raw:
            data[0][0] += 1
            data[1][0] += len(line)
            if line.strip().startswith(tuple(language.comments)):
                data[0][2] += 1
                data[1][2] += len(line)
            else:
                data[0][1] += 1
                data[1][1] += len(line)
    return (language, data)



def count_all(files):
    data = dict()
    total = [0, [0,0,0], [0,0,0]]
    for f in files:
        res = count_file(f)
        if res is None:
            continue
        if res[0] not in data:
            data[res[0]] = [0, [0, 0, 0], [0, 0, 0]]
        data[res[0]][0] += 1
        data[res[0]][1] = [sum(x) for x in zip(data[res[0]][1], res[1][0])]
        data[res[0]][2] = [sum(x) for x in zip(data[res[0]][2], res[1][1])]
        total[0] += 1
        total[1] = [sum(x) for x in zip(total[1], res[1][0])]
        total[2] = [sum(x) for x in zip(total[2], res[1][1])]
    #  for key, val in data.items():
        #  print(display.print_lang(key, 20))
    return data, total

def create_lang():
    global languages
    name = input("Name: ")
    ty = input("Type: ")
    color = input("Color: ")
    extensions = input("Extensions: ").split()
    comments = input("Comments: ").split()
    languages.append(Language(name, extensions, comments, ty, color, 0 ))

def sort_result(data, sort):
    if sort == "lang":
        return [data[0]] + sorted(data[1:-1], key=lambda x: ' '.join(x[0].split()[1:]).lower()) + [data[-1]]
    elif sort == "files":
        return [data[0]] + sorted(data[1:-1], key=lambda x: int(x[1]), reverse=True) + [data[-1]]
    elif sort == "lines":
        return [data[0]] + sorted(data[1:-1], key=lambda x: int(x[2]), reverse=True) + [data[-1]]
    elif sort == "codelines":
        return [data[0]] + sorted(data[1:-1], key=lambda x: int(x[3]), reverse=True) + [data[-1]]
    elif sort == "commentlines":
        return [data[0]] + sorted(data[1:-1], key=lambda x: int(x[4]), reverse=True) + [data[-1]]
    elif sort == "bytes":
        return [data[0]] + sorted(data[1:-1], key=lambda x: int(x[5]), reverse=True) + [data[-1]]
    elif sort == "codebytes":
        return [data[0]] + sorted(data[1:-1], key=lambda x: int(x[6]), reverse=True) + [data[-1]]
    elif sort == "commentbytes":
        return [data[0]] + sorted(data[1:-1], key=lambda x: int(x[7]), reverse=True) + [data[-1]]
    return data

def sort_fmt(sort):
    if sort == "bytes":
        return (2,0)
    elif sort == "codebytes":
        return (2,1)
    elif sort == "commentbytes":
        return (2,2)
    elif sort == "files":
        return (0)
    elif sort == "lines":
        return (1,0)
    elif sort == "codelines":
        return (1,1)
    elif sort == "commentlines":
        return (1,2)
    return (2,0)


def run_counter(args):
    if args.recurse is True:
        files = list()
        for dirpath, dirnames, filenames in os.walk(args.dir):
            for filename in [os.path.join(args.dir, dirpath, f) for f in filenames]:
                files.append(filename)
    else:
        files = [os.path.join(args.dir, f) for f in listdir(args.dir) if isfile(join(args.dir, f))]
    data, total = count_all(files)
    tmp = data
    data = dict()
    for key in sorted(tmp, key=lambda x: x.name.lower()):
        data[key] = tmp[key]
    table_data = [None] * (len(data) + 2)
    table_data[0] = ["Language","Files", "Lines", "Code Lines", "Comment Lines", "Bytes", "Code Bytes", "Comment Bytes", "Percentage"]
    i = 0
    sort = sort_fmt(args.sort)
    for key, value in data.items():
        table_data[i+1] = [""] * 9
        table_data[i+1][0] = " {}\u25cf{} {}".format(color.get_color(key.color), color.get_color(color.Color.DEFAULT), key.name)
        table_data[i+1][1] = "{}".format(value[0])
        table_data[i+1][2] = "{}".format(value[1][0])
        table_data[i+1][3] = "{}".format(value[1][1])
        table_data[i+1][4] = "{}".format(value[1][2])
        table_data[i+1][5] = "{}".format(value[2][0])
        table_data[i+1][6] = "{}".format(value[2][1])
        table_data[i+1][7] = "{}".format(value[2][2])
        if isinstance(sort, int):
            table_data[i+1][8] = "{:06.2%}".format(value[sort] / total[sort])
        else:
            table_data[i+1][8] = "{:06.2%}".format(value[sort[0]][sort[1]] / total[sort[0]][sort[1]])
        i += 1
    table_data[-1] = ["Total", "{}".format(total[0]), "{}".format(total[1][0]), "{}".format(total[1][1]), "{}".format(total[1][2]), "{}".format(total[2][0]), "{}".format(total[2][1]), "{}".format(total[2][2]), "100.0%"]
    table_data = sort_result(table_data, args.sort)
    if args.list is True:
        languages = [x for x in data]
        print()
        display.print_languages(languages)
        print()
    tab = table.Table(table_data, title_column=True, title_row=True)
    tab.set_column_alignment(0, table.Cell.Align.LEFT)
    for i in range(1, 9):
        tab.set_column_alignment(i, table.Cell.Align.RIGHT)
    if args.no_table_cell is False and args.table_cell is True:
        tab.draw_box = True
    if (args.no_zebra is False and args.zebra is True) or (args.no_zebra is False and tab.draw_box is False):
        tab.zebra = True
    if (args.no_table is False or args.table is True):
        tab.display()
    if (args.no_bar is False or args.bar is True):
        print()
        display.print_bar(data, total, sort, args.bar_width)
        print()


def main():
    rows, columns = os.popen("stty size", "r").read().split()
    sort_choices = ["lang", "files", "lines", "codelines", "commentlines", "bytes", "codebytes", "commentbytes"]
    parser = argparse.ArgumentParser(
            description="Counts lines/bytes of code in a given directory or file")
    parser.add_argument("-r", dest="recurse", action="store_true", help="Recursively finds all files")
    parser.add_argument("--languages", action="store_true", help="Lists all supported languages")
    parser.add_argument("--sort", type=str, nargs='?', default='bytes', help="Sorts result by data group", choices=sort_choices)
    parser.add_argument("--list", action="store_true", help="Lists languages in directory")
    parser.add_argument("dir", metavar="DIR", type=str, nargs='?', default=os.getcwd(), help="Directory to run analysis on")
    group = parser.add_argument_group("Display")
    group.add_argument("--table", action="store_true", help="Displays the table of values")
    group.add_argument("--no-table", action="store_true", help="Hides the table of values")
    group.add_argument("--bar", action="store_true", help="Displays bar indicating language splits")
    group.add_argument("--no-bar", action="store_true", help="Hides bar indicating language splits")
    group.add_argument("--zebra", action="store_true", help="Forces zebra line highlighting")
    group.add_argument("--no-zebra", action="store_true", help="Disables zebra line highlighting")
    group.add_argument("--table-cell", action="store_true", help="Draws table with unicode cells")
    group.add_argument("--no-table-cell", action="store_true", help="Does not draw table with unicode cells")
    group.add_argument("--bar-width", type=int, default=int(columns), help="Set the width of the bar diagram")
    args = parser.parse_args()
    load_languages()
    if args.languages:
        global languages
        display.print_languages(languages)
    else:
        run_counter(args)


if __name__ == "__main__":
    main()
