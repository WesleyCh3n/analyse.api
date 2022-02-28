#!/usr/bin/env python3
"""
purpose:
  export selection result
usage: python3 exporter.py -r cycle.start cycle.start -f <position file> -c <gait result> -s <out dir>
example: python3 exporter.py -r 1 11 -f tmp/v3.18.10-en-sample-0.csv -c tmp/v3.18.10-en-sample-1.csv -s result
example output:
{
  "ExportFile": "v3.18.10-en-sample-0-result.csv"
}
"""
import argparse
import json
import pandas as pd

from pathlib import Path

from module.cycle import createGaitCycleList, createCycleList

parser = argparse.ArgumentParser()
parser.add_argument("-r",
    type=int,
    nargs='+',
    action='append')
parser.add_argument("-f", type=str,)
parser.add_argument("-c", type=str,)
parser.add_argument("-s", type=str, default="file/csv/")

args = parser.parse_args()

if __name__ == "__main__":
    df = pd.read_csv(args.f)
    dfcy = pd.read_csv(args.c)
    df = df[df.columns.drop(list(df.filter(regex='support')))] # drop by regex

    # HACK: hard code read lt/rt/db file
    _, dfcy = createGaitCycleList(df, 'double_support')
    _, dflt = createCycleList(df, 'LT_single_support')
    _, dfrt = createCycleList(df, 'RT_single_support')
    _, dfdb = createCycleList(df, 'double_support')
    print(f'{dfcy=}')
    print(f'{dflt=}')
    print(f'{dfrt=}')
    print(f'{dfdb=}')

    maxMean = pd.concat([
        pd.concat([
            df[df['time'].between(dfcy.start[i], dfcy.start[i+1])]
                         .max()
                         .to_frame()
                         .T
            for i in range(r[0], r[1])
        ])
        for r in args.r
    ]).mean().drop(labels=['time']).to_frame().rename(index=lambda s: s + '_max')
    minMean = pd.concat([
        pd.concat([
            df[df['time'].between(dfcy.start[i], dfcy.start[i+1])]
                         .min()
                         .to_frame()
                         .T
            for i in range(r[0], r[1])
        ])
        for r in args.r
    ]).mean().drop(labels=['time']).to_frame().rename(index=lambda s: s + '_min')

    selection = ' '.join([f'{dfcy.start[r[0]]}-{dfcy.start[r[1]]}'
                          for r in args.r])

    concat_df = pd.concat([maxMean, minMean]).sort_index()
    result = pd.concat([pd.DataFrame({0: selection}, index=['Selection']),
                        concat_df])
    result = result.rename(columns={0: Path(args.f).stem})
    result.to_csv(Path(args.s)/f"{Path(args.f).stem}-result.csv")
    print(json.dumps({
        'ExportFile': f"{Path(args.f).stem}-result.csv"
    }, indent=2))
