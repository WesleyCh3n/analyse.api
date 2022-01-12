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
from module.preprocess import selectIndex, createSelectDF, convertMilliGToSI, separateSupportTime
from module.cycle import createGaitCycleList, createCycleList


parser = argparse.ArgumentParser()
parser.add_argument("-f",
    "--file",
    type=str)
parser.add_argument("-s",
    "--save",
    type=str)

args = parser.parse_args()

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
    date = re.findall(r'\d+-\d+-\d+-\d+-\d+', args.file)[0]
    name = re.findall(r'motion_(.*)_\d{4}.\d{2}.\d{2}', args.file)[0]
    num = re.findall(r'(\d+)\.csv', args.file)[0]

    print(json.dumps({
        'Result': saveDf(df.replace({True: 1, False: 0}), Path(args.save)/f'{date}_result_{name}_{num}.csv'),
        'CyGt': saveDf(dfcy, Path(args.save)/f'{date}_CyGt_{name}_{num}.csv'),
        'CyLt': saveDf(dflt, Path(args.save)/f'{date}_CyLt_{name}_{num}.csv'),
        'CyRt': saveDf(dfrt, Path(args.save)/f'{date}_CyRt_{name}_{num}.csv'),
        'CyDb': saveDf(dfdb, Path(args.save)/f'{date}_CyDb_{name}_{num}.csv'),
    }))

if __name__ == "__main__":
    main()
