#!/usr/bin/env python
# python ./scripts/selection_writer.py \
#    -f ./file/raw/v3.18.44-en-sample.csv -v "123123 1231 123 12"

import argparse
import json
from pathlib import Path
import shutil
import pandas as pd
import numpy as np

from module.selection import (
    check_selection_exist,
    add_selection_col,
)


def get_header(file: str, value: str):
    with open(file, mode="r+b") as f:
        contents = f.readlines()
        col_arr = contents[0].split(b",")
        val_arr = contents[1].split(b",")
        if len(col_arr) != 14:
            raise "Should add selection column first"
        if len(val_arr) < 14:
            val_arr[-1] = val_arr[-1][:-2]  # remove \r\n char
        elif len(val_arr) == 14:
            val_arr = val_arr[:-1]  # remove current selection

        col_arr[-1] = col_arr[-1][:-2] + b"\n"  # remove \r\n char
        col_arr[0] = b"\"type\""
        col_arr = col_arr[:7] + col_arr[9:]  # remove name
        val_arr = val_arr[:7] + val_arr[9:]  # remove name
        val_arr.append(f"\"{value}\"\n".encode("utf-8"))
        return [b",".join(col_arr), b",".join(val_arr), b"\n"]


def write_header(file: str, header: list):
    with open(file, mode="r+b") as f:
        contents = f.readlines()
        contents = header + contents
        f.seek(0, 0)
        f.writelines(contents)


def get_pos_dict(en, ch, repl, cols, orig_side=""):
    remap_dict = dict()
    for col in cols:
        if "Trajectories" in col or orig_side not in col:
            continue

        if en in col or ch in col:
            if (
                "Accel Sensor" in col
                or "传感器" in col
                or "course" in col
                or "pitch" in col
                or "roll" in col
            ):
                remap_dict[col] = (
                    col.replace("传感器", "Sensor")
                    .replace("LT ", "")
                    .replace("RT ", "")
                    .replace(en, repl)
                    .replace(ch, repl)
                )
            else:
                remap_dict[col] = col.replace(en, repl).replace(ch, repl)
    return remap_dict


def get_basic_dict(cols):
    remap_dict = dict()
    remap_dict["time"] = "time"
    remap_dict["Activity"] = "Activity"
    remap_dict["Marker"] = "Marker"
    for col in cols:
        if "Ultium Motion" in col:
            remap_dict[col] = "Ultium Motion.Switch 1 (On)"
    return remap_dict


def get_remap_dict(cols):
    d = {}
    d.update(get_basic_dict(cols))

    d.update(get_pos_dict("Pelvis", "骨盆", "L", cols))
    d.update(get_pos_dict("Lower spine", "脊椎下部", "T", cols))
    d.update(get_pos_dict("Upper spine", "脊椎上部", "Scapular LT", cols))
    d.update(get_pos_dict("Head", "头部", "Scapular RT", cols))
    d.update(get_pos_dict("Upper arm LT", "上臂", "SC", cols, "LT"))
    d.update(get_pos_dict("Forearm LT", "前臂", "HIP LT", cols, "LT"))
    d.update(get_pos_dict("Hand LT", "手", "Knee LT", cols, "LT"))
    d.update(get_pos_dict("Thigh LT", "大腿", "Shoulder LT", cols, "LT"))
    d.update(get_pos_dict("Shank LT", "胫骨", "PSIS LT", cols, "LT"))
    d.update(get_pos_dict("Foot LT", "脚", "Foot LT", cols, "LT"))

    d.update(get_pos_dict("Upper arm RT", "上臂", "C", cols, "RT"))
    d.update(get_pos_dict("Forearm RT", "前臂", "HIP RT", cols, "RT"))
    d.update(get_pos_dict("Hand RT", "手", "Knee RT", cols, "RT"))
    d.update(get_pos_dict("Thigh RT", "大腿", "Shoulder RT", cols, "RT"))
    d.update(get_pos_dict("Shank RT", "胫骨", "PSIS RT", cols, "RT"))
    d.update(get_pos_dict("Foot RT", "脚", "Foot RT", cols, "RT"))  # Contact!
    return d


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str)
parser.add_argument("-v", "--value", type=str)

args = parser.parse_args()

if __name__ == "__main__":
    save_dir = Path("./file/cleaning/")
    save_dir.mkdir(exist_ok=True)
    try:
        orig_file = Path(args.file)
        save_file = save_dir.joinpath(orig_file.name)

        # copy file
        shutil.copy(orig_file, save_file)

        # check selection column exist
        if not check_selection_exist(save_file):
            ranges = add_selection_col(save_file)

        # update selection value
        header = get_header(save_file, args.value)
        # remove name and last name

        raw_data = pd.read_csv(
            save_file, skiprows=np.array([0, 1, 2]), low_memory=False
        )

        cols = raw_data.columns
        remap_d = get_remap_dict(cols)
        # with open("map.json", "w") as f:
        # json.dump(remap_d, f, indent=2, ensure_ascii=False)

        clean_df = raw_data[list(remap_d.keys())].rename(columns=remap_d)
        clean_df.to_csv(save_file, index=False)

        write_header(save_file, header)

        print(
            json.dumps(
                {
                    "msg": "Success",
                    "clean_file": str(save_file.name),
                }
            )
        )
    except Exception as e:
        raise e
