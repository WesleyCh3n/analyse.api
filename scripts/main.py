#!/usr/bin/env python3

import argparse
from filter import filter
from exporter import export
from concater import concat
from selection_writer import sel_writer


def parse_args():
    parser = argparse.ArgumentParser()
    # select module
    subparser = parser.add_subparsers(dest="analyze")
    subparser.required = True

    parser_filter = subparser.add_parser("filter")
    parser_filter.add_argument("-f", "--file", type=str, required=True)
    parser_filter.add_argument("-s", "--save", type=str, required=True)

    parser_export = subparser.add_parser("export")
    parser_export.add_argument("-f", "--file", type=str, required=True)
    parser_export.add_argument(
        "-s", "--save", type=str, default="file/csv/", required=True
    )
    parser_export.add_argument(
        "-r", "--range", type=int, nargs="+", action="append", required=True
    )

    parser_concat = subparser.add_parser("concat")
    parser_concat.add_argument(
        "-f", "--files", type=str, nargs="+", required=True
    )
    parser_concat.add_argument(
        "-s", "--save", type=str, default="file/export/", required=True
    )

    parser_swrite = subparser.add_parser("swrite")
    parser_swrite.add_argument("-f", "--file", type=str, required=True)
    parser_swrite.add_argument("-v", "--value", type=str, required=True)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    if args.analyze == "filter":
        filter(args.file, args.save)
    elif args.analyze == "export":
        export(args.file, args.save, args.range)
    elif args.analyze == "concat":
        concat(args.files, args.save)
    elif args.analyze == "swrite":
        sel_writer(args.file, args.value)
