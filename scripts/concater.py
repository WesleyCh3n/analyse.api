#!/usr/bin/env python3

import argparse
import json
import pandas as pd

from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    type=str,
    nargs="+",
)
parser.add_argument("-s", type=str, default="file/export/")

args = parser.parse_args()

if __name__ == "__main__":
    df = pd.concat([pd.read_csv(f, index_col=0) for f in args.f], axis=1)
    df.to_csv(Path(args.s) / "concat.csv")
    print(json.dumps({"ConcatFile": "concat.csv"}))
