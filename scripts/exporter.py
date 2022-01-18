#!/usr/bin/env python3

import argparse
import json
import pandas as pd

from pathlib import Path


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
    cygt = pd.read_csv(args.c)
    df = df[df.columns.drop(list(df.filter(regex='support')))] # drop by regex

    maxMean = pd.concat([
        pd.concat([
            df[df['time'].between(cygt.start[i], cygt.start[i+1])]
                         .max()
                         .to_frame()
                         .T
            for i in range(r[0], r[1])
        ])
        for r in args.r
    ]).mean().drop(labels=['time']).to_frame().rename(index=lambda s: s + '_max')
    minMean = pd.concat([
        pd.concat([
            df[df['time'].between(cygt.start[i], cygt.start[i+1])]
                         .min()
                         .to_frame()
                         .T
            for i in range(r[0], r[1])
        ])
        for r in args.r
    ]).mean().drop(labels=['time']).to_frame().rename(index=lambda s: s + '_min')

    selection = ' '.join([f'{cygt.start[r[0]]}-{cygt.start[r[1]]}'
                          for r in args.r])

    concat_df = pd.concat([maxMean, minMean]).sort_index()
    result = pd.concat([pd.DataFrame({0: selection}, index=['Selection']),
                        concat_df])
    result = result.rename(columns={0: Path(args.f).stem})
    result.to_csv(Path(args.s)/f"{Path(args.f).stem}-result.csv")
    print(json.dumps({
        'ExportFile': f"{Path(args.f).stem}-result.csv"
    }))
