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
from numpy import array
from module.preprocess import createSelectDF, convertMilliGToSI, separateSupportTime
from module.cycle import createGaitCycleList, createCycleList

parser = argparse.ArgumentParser()
parser.add_argument("-f",
    "--file",
    type=str)
parser.add_argument("-s",
    "--save",
    type=str)

args = parser.parse_args()

POSITION = ['Pelvis', "Lower spine", "Upper spine", "Head"]
AXIS = ['X', 'Y', 'Z']

def argsProcess():
    date = re.findall(r'\d+-\d+-\d+-\d+-\d+', args.file)[0]
    name = re.findall(r'motion_(.*)_\d{4}.\d{2}.\d{2}', args.file)[0]
    num = re.findall(r'(\d+)\.csv', args.file)[0]
    return date, name, num

def main():
    # NOTE:
    # col: [time, acceleration[CTLS], contact[RL]]
    zipObj = zip(np.repeat(array(POSITION), 3), AXIS * 3) # HACK: zip repeat
    sel_dict = {
        # init index
        'time': 'time', # time index
        'Noraxon MyoMotion-Segments-Foot RT-Contact': 'RT_contact', # R contact index
        'Noraxon MyoMotion-Segments-Foot LT-Contact': 'LT_contact', # L contact index
    }
    a_label_mG, a_label_SI = [], []
    for pos, ax in zipObj:
        # select index
        sel_dict[f'{pos} Accel Sensor {ax} (mG)'] = f'{pos}_A_{ax}_mG'
        sel_dict[f'Noraxon MyoMotion-Segments-{pos}-Gyroscope-{ax.lower()} (deg/s)'] = f'{pos}_Gyro_{ax}'
        a_label_mG.append(f'{pos}_A_{ax}_mG')
        a_label_SI.append(f'{pos}_A_{ax}')

    raw_data = pd.read_csv(args.file, skiprows=array([0,1,2]), low_memory=False)
    df = createSelectDF(raw_data, sel_dict) # select columns
    df[['RT_contact', 'LT_contact']] = df[['RT_contact', 'LT_contact']].replace({1000: True, 0: False})

    df = convertMilliGToSI(df, a_label_mG, a_label_SI) # INFO: out: [...f'{pos}_A_{ax}']
    df = separateSupportTime(df) # INFO: out: ['double_support', 'RT_single_support', 'LT_single_support']
    df = df.drop(columns=a_label_mG + ['RT_contact', 'LT_contact']) # drop unnecessary columns

    # create cycle list
    _, dfcy = createGaitCycleList(df, 'double_support')
    _, dflt = createCycleList(df, 'LT_single_support')
    _, dfrt = createCycleList(df, 'RT_single_support')
    _, dfdb = createCycleList(df, 'double_support')

    #=================================================================#
    # Export
    date, name, num = argsProcess()
    rslt_path = Path(args.save) / f'{date}_result_{name}_{num}.csv'
    cyc_path = Path(args.save) / f'{date}_cycle_{name}_{num}.csv'
    lt_path = Path(args.save) / f'{date}_cycle-lt_{name}_{num}.csv'
    rt_path = Path(args.save) / f'{date}_cycle-rt_{name}_{num}.csv'
    db_path = Path(args.save) / f'{date}_cycle-db_{name}_{num}.csv'

    df.replace({True: 1, False: 0}).to_csv(rslt_path, index=False)
    dfcy.to_csv(cyc_path, index=False)
    dflt.to_csv(lt_path, index=False)
    dfrt.to_csv(rt_path, index=False)
    dfdb.to_csv(db_path, index=False)

    print(rslt_path)
    print(cyc_path)
    print(lt_path)
    print(rt_path)
    print(db_path)

if __name__ == "__main__":
    main()
