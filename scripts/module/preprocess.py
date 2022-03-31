#!/usr/bin/env python3

import pandas as pd


def get_basic_dict(cols):
    remap_dict = dict()
    remap_dict["time"] = "time"
    for col in cols:
        if "Contact" in col:
            if "Foot LT" in col:
                remap_dict[col] = "LT_contact"
            elif "Foot RT" in col:
                remap_dict[col] = "RT_contact"
            elif "脚 左" in col:
                remap_dict[col] = "LT_contact"
            elif "脚 右" in col:
                remap_dict[col] = "RT_contact"
    return remap_dict


def get_pos_dict(en, ch, cols):
    remap_dict = dict()
    for col in cols:
        if en in col or ch in col:
            if " Accel " in col:
                if " X " in col:
                    remap_dict[col] = f"{en}_A_X_mG"
                if " Y " in col:
                    remap_dict[col] = f"{en}_A_Y_mG"
                if " Z " in col:
                    remap_dict[col] = f"{en}_A_Z_mG"
            if "-Gyroscope-" in col:
                if "-x " in col:
                    remap_dict[col] = f"{en}_Gyro_X"
                if "-y " in col:
                    remap_dict[col] = f"{en}_Gyro_Y"
                if "-z " in col:
                    remap_dict[col] = f"{en}_Gyro_Z"
    return remap_dict


def selectIndex(cols):
    # dict: key->old_name, value->new_name
    remap_dict = {}
    remap_dict.update(get_pos_dict("Pelvis", "骨盆", cols))
    remap_dict.update(get_pos_dict("Upper spine", "脊椎上部", cols))
    remap_dict.update(get_pos_dict("Lower spine", "脊椎下部", cols))
    remap_dict.update(get_pos_dict("Head", "头部", cols))
    remap_dict.update(get_basic_dict(cols))
    return remap_dict


def createSelectDF(df, sel_dict: dict) -> pd.DataFrame:
    """
    sel_dict: {
      'time': 'time',
      'original_index_name': 'perfered_index_name',
    }
    """
    selected_df = df[list(sel_dict.keys())].rename(columns=sel_dict)
    selected_df[["RT_contact", "LT_contact"]] = selected_df[
        ["RT_contact", "LT_contact"]
    ].replace({1000: True, 0: False})
    return selected_df


def convertMilliGToSI(df) -> pd.DataFrame:
    factor = 9.80665 * 10 ** (-3)
    for col in df.columns:
        if "mG" in col:
            df[col] = (
                df[col] * factor
                if "_X_" not in col
                else df[col] * factor - 9.80665
            )
            df.rename(columns={col: col.replace("_mG", "")}, inplace=True)
    return df


def separateSupportTime(df):
    df["double_support"] = df["LT_contact"] & df["RT_contact"]
    df["single_support"] = ~df["double_support"]
    df["RT_single_support"] = df["RT_contact"] & df["single_support"]
    df["LT_single_support"] = df["LT_contact"] & df["single_support"]

    df = df.drop(columns=["RT_contact", "LT_contact"])

    return df
