#!/usr/bin/env python3

# purpose: python3 main.py -f <file.csv>
# output:
#   1. support + acceleration.csv
#   3. cycle.csv


import pandas as pd
import numpy as np
import argparse
import re

from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-f",
    "--file",
    type=str)
parser.add_argument("-s",
    "--save",
    type=str)

args = parser.parse_args()

def createSelectDF(df, sel_dict: dict) -> pd.DataFrame:
    """
  sel_dict: {
    'time': 'time',
    'original_index_name': 'perfered_index_name',
  }
  """
    return df[list(sel_dict.keys())].rename(columns=sel_dict)

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

def createGaitCycleList(df, step=2, dsIndex="double_support"):
    doubleSupportArr = df[dsIndex].values
    mask = (doubleSupportArr[:-1]==False) & (doubleSupportArr[1:]==True)
    doubleSupportStartIndex = np.where(mask)[0] + 1
    gStart = doubleSupportStartIndex[::step]

    return list(zip(gStart, gStart[1:])), df.loc[gStart, 'time'].copy()

if __name__ == "__main__":
    # NOTE:
    # col: [time, acceleration[CTLS], contact[RL]]
    positions = ['Pelvis', "Lower spine", "Upper spine", "Head"]
    axis = ['X', 'Y', 'Z']
    zipObj = zip(np.repeat(positions, 3), axis * 3) # HACK: zip repeat
    sel_dict = {
        'time': 'time', # time index
        'Noraxon MyoMotion-Segments-Foot RT-Contact': 'RT_contact', # R contact index
        'Noraxon MyoMotion-Segments-Foot LT-Contact': 'LT_contact', # L contact index
    }
    a_label_mG, a_label_SI = [], []
    for pos, ax in zipObj:
        sel_dict[f'{pos} Accel Sensor {ax} (mG)'] = f'{pos}_A_{ax}_mG'
        a_label_mG.append(f'{pos}_A_{ax}_mG')
        a_label_SI.append(f'{pos}_A_{ax}')

    raw_data = pd.read_csv(args.file, skiprows=[0,1,2], low_memory=False)
    df = createSelectDF(raw_data, sel_dict)
    df[['RT_contact', 'LT_contact']] = df[['RT_contact', 'LT_contact']].replace({1000: True, 0: False})

    df = convertMilliGToSI(df, a_label_mG, a_label_SI) # NOTE: out: [...f'{pos}_A_{ax}']
    df = separateSupportTime(df) # NOTE: out: ['double_support', 'RT_single_support', 'LT_single_support']
    cycle, dfCycle = createGaitCycleList(df, 2, 'double_support')

    # Export
    date = re.findall(r'\d+-\d+-\d+-\d+-\d+', args.file)[0]
    name = re.findall(r'motion_(.*)_\d{4}.\d{2}.\d{2}', args.file)[0]
    num = re.findall(r'(\d+)\.csv', args.file)[0]
    df[[
        'time',
        'double_support',
        'RT_single_support',
        'LT_single_support'
    ] + a_label_SI ].replace({True: 1, False: 0}).to_csv(Path(args.save) / f'{date}_result_{name}_{num}.csv', index=False)

    # dfCycle.index.name = 'index'
    dfCycle.to_csv(Path(args.save) / f'{date}_cycle_{name}_{num}.csv')

    print(Path(args.save) / f'{date}_result_{name}_{num}.csv')
    print(Path(args.save) / f'{date}_cycle_{name}_{num}.csv')
