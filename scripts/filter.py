#!/usr/bin/env python3
"""
purpose:
  create preprocess node's 6 axis data, cycle data, preselected range.
usage: python3 filter.py -f <file.csv> -s <out dir>
example: python3 filter.py -f ../file/raw/v3.18.10-en-sample.csv -s ./tmp
example output:
{
  "FltrFile": {
    "rslt": "v3.18.10-en-sample-0.csv",
    "cyGt": "v3.18.10-en-sample-1.csv",
    "cyLt": "v3.18.10-en-sample-2.csv",
    "cyRt": "v3.18.10-en-sample-3.csv",
    "cyDb": "v3.18.10-en-sample-4.csv"
  },
  "Range": []
}
"""
import argparse
import pandas as pd
import json

from pathlib import Path
from numpy import array

from module.cycle import createGaitCycleList, createCycleList
from module.preprocess import selectIndex
from module.preprocess import createSelectDF
from module.preprocess import convertMilliGToSI
from module.preprocess import separateSupportTime
from module.selection import check_selection_exist
from module.selection import check_value_exist
from module.selection import add_selection_col
from module.selection import get_selection


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str)
parser.add_argument("-s", "--save", type=str)

args = parser.parse_args()


def saveDf(df, path):
    # mkdir
    Path(args.save).mkdir(exist_ok=True)
    try:
        df.to_csv(Path(args.save) / path, index=False)
    except:
        return "Error: create csv failed"

    return str(path)


def main():
    # checking header selection section
    if not check_selection_exist(args.file):
        ranges = add_selection_col(args.file)
    else:
        if check_value_exist(args.file):
            ranges = get_selection(args.file)
        else:
            ranges = []

    raw_data = pd.read_csv(
        args.file, skiprows=array([0, 1, 2]), low_memory=False
    )
    sel_dict = selectIndex(raw_data.columns)
    df = createSelectDF(raw_data, sel_dict)
    df = convertMilliGToSI(df)
    df = separateSupportTime(df)

    # create cycle list
    _, dfcy = createGaitCycleList(df, "double_support")
    _, dflt = createCycleList(df, "LT_single_support")
    _, dfrt = createCycleList(df, "RT_single_support")
    _, dfdb = createCycleList(df, "double_support")

    # ================================================================= #
    # Export
    in_filename = Path(args.file).stem
    print(
        json.dumps(
            {
                "FltrFile": {
                    "rslt": saveDf(
                        df.replace({True: 1, False: 0}), f"{in_filename}-0.csv"
                    ),
                    "cyGt": saveDf(dfcy, f"{in_filename}-1.csv"),
                    "cyLt": saveDf(dflt, f"{in_filename}-2.csv"),
                    "cyRt": saveDf(dfrt, f"{in_filename}-3.csv"),
                    "cyDb": saveDf(dfdb, f"{in_filename}-4.csv"),
                },
                "Range": ranges,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
