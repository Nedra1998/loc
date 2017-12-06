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


class Language(object):

    def __init__(self, name=str(), ext=list(), com=list(), type="(null)", color="#000000", id=0):
        self.name = name
        self.extensions = ext
        self.comments = com
        self.id = id
        self.color = color
        self.type = type

    def __repr__(self):
        return "<[{}]{}: {}, {}, {}>".format(self.id, self.name, self.extensions, self.comments, self.color)


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
    print(data)
    print(total)
    for key, val in data.items():
        print(display.print_lang(key, 20))

def create_lang():
    global languages
    name = input("Name: ")
    ty = input("Type: ")
    color = input("Color: ")
    extensions = input("Extensions: ").split()
    comments = input("Comments: ").split()
    languages.append(Language(name, extensions, comments, ty, color, 0 ))


def run_counter(path, recurse):
    if recurse is True:
        files = list()
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in [os.path.join(path, dirpath, f) for f in filenames]:
                files.append(filename)
    else:
        files = [os.path.join(path, f) for f in listdir(path) if isfile(join(path, f))]
    #  import pprint
    #  pprint.pprint(files)
    count_all(files)


def main():
    parser = argparse.ArgumentParser(
            description="Counts lines/bytes of code in a given directory or file")
    parser.add_argument("-r", dest="recurse", action="store_true", help="Recursively finds all files")
    parser.add_argument("--languages", action="store_true", help="Lists all supported languages")
    parser.add_argument("dir", type=str, nargs='?', default=os.getcwd(), help="Directory to run analysis on")
    args = parser.parse_args()
    load_languages()
    if args.languages:
        global languages
        display.print_languages(languages)
    else:
        run_counter(args.dir, args.recurse)

if __name__ == "__main__":
    main()
