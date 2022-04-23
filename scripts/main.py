#!/usr/bin/env python3

import argparse
from filter import filter
from exporter import export
from concater import concat
from selection_writer import sel_writer

parser = argparse.ArgumentParser()
# select module
parser.add_argument("-t", "--type", type=str)

# filter
parser.add_argument("-f", "--file", type=str)
parser.add_argument("-s", "--save", type=str)

# export
parser.add_argument("-r", "--range", type=int, nargs="+", action="append")

# concat
parser.add_argument("-c", "--concat", type=str, nargs="+",)

# selection writer
# parser.add_argument("-f", "--file", type=str)
parser.add_argument("-v", "--value", type=str)

args = parser.parse_args()


if __name__ == "__main__":
    if args.type == "filter":
        filter(args.file, args.save)
    elif args.type == "export":
        export(args.file, args.save, args.range)
    elif args.type == "concat":
        concat(args.concat, args.save)
    elif args.type == "swrite":
        sel_writer(args.file, args.value)
