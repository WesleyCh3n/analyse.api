#!/usr/bin/env python3

import pandas as pd

def createSelectDF(df, sel_dict: dict) -> pd.DataFrame:
    """
  sel_dict: {
    'time': 'time',
    'original_index_name': 'perfered_index_name',
  }
  """
    selected_df = df[list(sel_dict.keys())].rename(columns=sel_dict)
    selected_df[['RT_contact', 'LT_contact']] = selected_df[['RT_contact', 'LT_contact']].replace({1000: True, 0: False})
    return selected_df

def convertMilliGToSI(df, index: list, out_index: list) -> pd.DataFrame:
    factor = 9.80665 * 10**(-3)
    for i, o in zip(index, out_index):
        df[o] = df[i] * factor
        if 'x' in i:
            df[o] = df[i] * factor - 9.80665
    return df

def separateSupportTime(df):
    df['double_support'] = df['LT_contact'] & df['RT_contact']
    df['single_support'] = ~df['double_support']
    df['RT_single_support'] = df['RT_contact'] & df['single_support']
    df['LT_single_support'] = df['LT_contact'] & df['single_support']

    return df
