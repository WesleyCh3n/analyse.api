#!/usr/bin/env python3

import argparse
import pandas as pd
# import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-r",
    type=int,
    nargs='+',
    action='append')

args = parser.parse_args()

if __name__ == "__main__":
    cygt = pd.read_csv('../file/csv/2021-09-26-18-36_CyGt_Dr Tsai_1.csv')
    df = pd.read_csv('../file/csv/2021-09-26-18-36_result_Dr Tsai_1.csv')
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
    ]).mean().drop(labels=['time']).to_frame(name='max')
    minMean = pd.concat([
        pd.concat([
            df[df['time'].between(cygt.start[i], cygt.start[i+1])]
                         .min()
                         .to_frame()
                         .T
            for i in range(r[0], r[1])
        ])
        for r in args.r
    ]).mean().drop(labels=['time']).to_frame(name='min')

    print(pd.concat([maxMean, minMean], axis=1))
