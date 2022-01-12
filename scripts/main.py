#!/usr/bin/env python3

# purpose: python3 main.py -f <file.csv> -s <out dir>
# output:
#   1. support + acceleration.csv
#   3. cycle.csv


import pandas as pd
import numpy as np
import argparse
import re
import json

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

def argsProcess():
    date = re.findall(r'\d+-\d+-\d+-\d+-\d+', args.file)[0]
    name = re.findall(r'motion_(.*)_\d{4}.\d{2}.\d{2}', args.file)[0]
    num = re.findall(r'(\d+)\.csv', args.file)[0]
    return date, name, num

def selectIndex(position):
    # [time, [LR] contact, [position] accel/gyro]
    sel_dict = {
        # init index
        'time': 'time', # time index
        'Noraxon MyoMotion-Segments-Foot RT-Contact': 'RT_contact', # R contact index
        'Noraxon MyoMotion-Segments-Foot LT-Contact': 'LT_contact', # L contact index
    }
    for pos, ax in zip(np.repeat(array(position), 3), ['X','Y','Z'] * 3): # HACK: zip repeat:
        # Acceleration [XYZ]
        sel_dict[f'{pos} Accel Sensor {ax} (mG)'] = f'{pos}_A_{ax}_mG'
        # Gyroscope [XYZ]
        sel_dict[f'Noraxon MyoMotion-Segments-{pos}-Gyroscope-{ax.lower()} (deg/s)'] = f'{pos}_Gyro_{ax}'
    return sel_dict

def saveDf(df, path):
    try:
        df.to_csv(path, index=False)
    except:
        return "Error"

    return str(path)

def main():
    position = ['Pelvis', 'Lower spine', 'Upper spine', 'Head']
    sel_dict = selectIndex(position)

    raw_data = pd.read_csv(args.file, skiprows=array([0,1,2]), low_memory=False)
    df = createSelectDF(raw_data, sel_dict) # select columns

    a_label_mG = [f'{pos}_A_{ax}_mG' for pos, ax in zip(np.repeat(array(position), 3), ['X','Y','Z'] * 3)]
    a_label_SI = [f'{pos}_A_{ax}' for pos, ax in zip(np.repeat(array(position), 3), ['X','Y','Z'] * 3)]
    df = convertMilliGToSI(df, a_label_mG, a_label_SI)
    df = separateSupportTime(df)
    df = df.drop(columns=a_label_mG + ['RT_contact', 'LT_contact']) # drop unnecessary columns

    # create cycle list
    _, dfcy = createGaitCycleList(df, 'double_support')
    _, dflt = createCycleList(df, 'LT_single_support')
    _, dfrt = createCycleList(df, 'RT_single_support')
    _, dfdb = createCycleList(df, 'double_support')

    #=================================================================#
    # Export
    date, name, num = argsProcess()
    print(json.dumps({
        'Result': saveDf(df.replace({True: 1, False: 0}), Path(args.save)/f'{date}_result_{name}_{num}.csv'),
        'CyGt': saveDf(dfcy, Path(args.save)/f'{date}_CyGt_{name}_{num}.csv'),
        'CyLt': saveDf(dflt, Path(args.save)/f'{date}_CyLt_{name}_{num}.csv'),
        'CyRt': saveDf(dfrt, Path(args.save)/f'{date}_CyRt_{name}_{num}.csv'),
        'CyDb': saveDf(dfdb, Path(args.save)/f'{date}_CyDb_{name}_{num}.csv'),
    }))
    # rslt_path = Path(args.save) / f'{date}_result_{name}_{num}.csv'
    # cyc_path = Path(args.save) / f'{date}_cycle_{name}_{num}.csv'
    # lt_path = Path(args.save) / f'{date}_cycle-lt_{name}_{num}.csv'
    # rt_path = Path(args.save) / f'{date}_cycle-rt_{name}_{num}.csv'
    # db_path = Path(args.save) / f'{date}_cycle-db_{name}_{num}.csv'

    # df.replace({True: 1, False: 0}).to_csv(rslt_path, index=False)
    # dfcy.to_csv(cyc_path, index=False)
    # dflt.to_csv(lt_path, index=False)
    # dfrt.to_csv(rt_path, index=False)
    # dfdb.to_csv(db_path, index=False)

    # TODO: fix with json dump
    # print(rslt_path)
    # print(cyc_path)
    # print(lt_path)
    # print(rt_path)
    # print(db_path)
    # print(json.dumps({
    # 'rslt_path': str(rslt_path),
    # 'cyc_path': str(cyc_path),
    # 'lt_path': str(lt_path),
    # 'rt_path': str(rt_path),
    # 'db_path': str(db_path),
    # }))

if __name__ == "__main__":
    main()
