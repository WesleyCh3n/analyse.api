#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-r",
    type=int,
    nargs='+',
    action='append')

args = parser.parse_args()
print(args.r)
