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
from functools import reduce
import json
import pandas as pd

from pathlib import Path

from module.cycle import createGaitCycleList, createCycleList


def create_selection_mask(df, dfcy, walk_range: list):
    mask = []
    for (a, b) in walk_range:
        s_time, e_time = dfcy.start[a], dfcy.start[b]
        mask.append(df["start"].between(s_time, e_time, inclusive="left"))
    return mask


def export(file: str, save_dir: str, walk_range: list):
    df = pd.read_csv(file)
    # dfcy = pd.read_csv(args.c)

    # HACK: hard code read lt/rt/db file
    _, dfcy = createGaitCycleList(df, "double_support")
    _, dflt = createCycleList(df, "LT_single_support")
    _, dfrt = createCycleList(df, "RT_single_support")
    _, dfdb = createCycleList(df, "double_support")

    df = df.drop(columns=list(df.filter(regex="support")))

    maxMean = (
        pd.concat(
            [
                pd.concat(
                    [
                        df[df["time"].between(dfcy.start[i], dfcy.start[i + 1])]
                        .max()
                        .to_frame()
                        .T
                        for i in range(r[0], r[1])
                    ]
                )
                for r in walk_range
            ]
        )
        .mean()
        .drop(labels=["time"])
        .to_frame()
        .rename(index=lambda s: s + "_max")
    )

    minMean = (
        pd.concat(
            [
                pd.concat(
                    [
                        df[df["time"].between(dfcy.start[i], dfcy.start[i + 1])]
                        .min()
                        .to_frame()
                        .T
                        for i in range(r[0], r[1])
                    ]
                )
                for r in walk_range
            ]
        )
        .mean()
        .drop(labels=["time"])
        .to_frame()
        .rename(index=lambda s: s + "_min")
    )

    mask = create_selection_mask(dflt, dfcy, walk_range)
    df_filter = dflt[reduce(lambda x, y: x | y, mask)]
    dflt_mean = pd.DataFrame(
        {0: (df_filter.end - df_filter.start).mean()},
        index=["LT_single_support"],
    )
    mask = create_selection_mask(dfrt, dfcy, walk_range)
    df_filter = dfrt[reduce(lambda x, y: x | y, mask)]
    dfrt_mean = pd.DataFrame(
        {0: (df_filter.end - df_filter.start).mean()},
        index=["RT_single_support"],
    )
    mask = create_selection_mask(dfdb, dfcy, walk_range)
    df_filter = dfdb[reduce(lambda x, y: x | y, mask)]
    dfdb_mean = pd.DataFrame(
        {0: (df_filter.end - df_filter.start).mean()}, index=["double_support"]
    )
    mask = create_selection_mask(dfcy, dfcy, walk_range)
    df_filter = dfcy[reduce(lambda x, y: x | y, mask)]
    dfcy_mean = pd.DataFrame(
        {0: (df_filter.end - df_filter.start).mean()}, index=["gait"]
    )
    dfss_mean = pd.DataFrame(
        {0: (dflt_mean.iloc[0, 0] + dfrt_mean.iloc[0, 0])},
        index=["single_support"]
    )

    # concat min max's mean
    concat_df = pd.concat([maxMean, minMean]).sort_index()
    # selection range
    selection = " ".join(
        [f"{dfcy.start[r[0]]}-{dfcy.start[r[1]]}" for r in walk_range]
    )
    df_selection = pd.DataFrame({0: selection}, index=["Selection"])
    # concat all df
    result = pd.concat(
        [df_selection, dfcy_mean, dflt_mean, dfrt_mean, dfss_mean, dfdb_mean,
            concat_df]
    )
    result = result.rename(columns={0: Path(file).stem})
    result.to_csv(Path(save_dir) / f"{Path(file).stem}-result.csv")
    print(
        json.dumps({"ExportFile": f"{Path(file).stem}-result.csv"}, indent=2)
    )


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-r", type=int, nargs="+", action="append")
    # parser.add_argument(
    #     "-f",
    #     type=str,
    # )
    # parser.add_argument(
    #     "-c",
    #     type=str,
    # )  # TODO: unused, remove this arg
    # parser.add_argument("-s", type=str, default="file/csv/")
    #
    # args = parser.parse_args()
    export()
