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

    # add start and end index for drawing
    dfIndex = np.r_[0, gStart, df.shape[0]-1]
    dfStep = df.loc[dfIndex, 'time'].copy().to_frame(name="start").reset_index(drop=True)
    dfStep['end'] = dfStep.shift(-1)

    return list(zip(gStart, gStart[1:])), dfStep

def createCycleList(df, dsIndex):
    arr = df[dsIndex].values
    mask = (arr[:-1]==False) & (arr[1:]==True)
    startIndex = np.where(mask)[0] + 1
    mask = (arr[:-1]==True) & (arr[1:]==False)
    endIndex = np.where(mask)[0] + 1

    if dsIndex == 'double_support':
        startIndex, endIndex = startIndex[:-1], endIndex[1:]

    dfStep = df.loc[startIndex, 'time'].copy().to_frame(name="start").reset_index(drop=True)
    dfStep['end'] = df.loc[endIndex, 'time'].copy().to_frame(name="end").reset_index(drop=True)

    return [(s, e) for s, e in zip(startIndex, endIndex)], dfStep

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
        sel_dict[f'Noraxon MyoMotion-Segments-{pos}-Gyroscope-{ax.lower()} (deg/s)'] = f'{pos}_Gyro_{ax}'
        a_label_mG.append(f'{pos}_A_{ax}_mG')
        a_label_SI.append(f'{pos}_A_{ax}')

    raw_data = pd.read_csv(args.file, skiprows=[0,1,2], low_memory=False)

    # select columns
    df = createSelectDF(raw_data, sel_dict)

    # convert to SI Unit
    df = convertMilliGToSI(df, a_label_mG, a_label_SI) # NOTE: out: [...f'{pos}_A_{ax}']

    # calculate support time
    df[['RT_contact', 'LT_contact']] = df[['RT_contact', 'LT_contact']].replace({1000: True, 0: False})
    df = separateSupportTime(df) # NOTE: out: ['double_support', 'RT_single_support', 'LT_single_support']

    # drop unnecessary columns
    df = df.drop(columns=a_label_mG + ['RT_contact', 'LT_contact'])

    # create cycle list
    cycle, dfCycle = createGaitCycleList(df, 2, 'double_support')
    _, dflt = createCycleList(df, "LT_single_support")
    _, dfrt = createCycleList(df, "RT_single_support")
    _, dfdb = createCycleList(df, "double_support")

    #=================================================================#
    # Export
    date = re.findall(r'\d+-\d+-\d+-\d+-\d+', args.file)[0]
    name = re.findall(r'motion_(.*)_\d{4}.\d{2}.\d{2}', args.file)[0]
    num = re.findall(r'(\d+)\.csv', args.file)[0]

    rslt_path = Path(args.save) / f'{date}_result_{name}_{num}.csv'
    cyc_path = Path(args.save) / f'{date}_cycle_{name}_{num}.csv'
    lt_path = Path(args.save) / f'{date}_cycle-lt_{name}_{num}.csv'
    rt_path = Path(args.save) / f'{date}_cycle-rt_{name}_{num}.csv'
    db_path = Path(args.save) / f'{date}_cycle-db_{name}_{num}.csv'

    df.replace({True: 1, False: 0}).to_csv(rslt_path, index=False)
    dfCycle.to_csv(cyc_path, index=False)
    dflt.to_csv(lt_path, index=False)
    dfrt.to_csv(rt_path, index=False)
    dfdb.to_csv(db_path, index=False)

    print(rslt_path)
    print(cyc_path)
    print(lt_path)
    print(rt_path)
    print(db_path)
