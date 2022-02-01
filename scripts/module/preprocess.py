#!/usr/bin/env python3

import pandas as pd
import numpy as np
from numpy import array

def selectIndex(position):
    # [time, [LR] contact, [position] accel/gyro]
    sel_dict = {
        # init index
        'time': 'time', # time index
        'RT Contact': 'RT_contact', # R contact index
        'LT Contact': 'LT_contact', # L contact index
    }
    for pos, ax in zip(np.repeat(array(position), 3), ['X','Y','Z'] * 3): # HACK: zip repeat:
        # Acceleration [XYZ]
        sel_dict[f'{pos} Accel Sensor {ax} (mG)'] = f'{pos}_A_{ax}_mG'
        # Gyroscope [XYZ]
        sel_dict[f'Noraxon MyoMotion-Segments-{pos}-Gyroscope-{ax.lower()} (deg/s)'] = f'{pos}_Gyro_{ax}'
    return sel_dict

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
