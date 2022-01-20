#!/usr/bin/env python

import argparse
import json

from module.selection import update_value


parser = argparse.ArgumentParser()
parser.add_argument("-f",
    "--file",
    type=str)
parser.add_argument("-v",
    "--value",
    type=str)

args = parser.parse_args()

if __name__ == "__main__":
    try:
        update_value(args.file, args.value)
        print(json.dumps({
            "msg": "Success",
        }))
    except Exception as e:
        print(json.dumps({
            "msg": f'{e}',
        }))
