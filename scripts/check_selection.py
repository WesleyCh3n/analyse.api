#!/usr/bin/env python

import csv

filename = "./file/raw/2021-09-26-18-36_ultium_motion_Dr Tsai_2021.09.26 Dr. Tsai_1.csv"
fieldnames = []
with open(filename, mode='r', encoding='utf-8-sig') as f:
    csv_reader = csv.DictReader(f)
    obj = next(csv_reader)
    if "selection" in obj:
        print('yes')

with open(filename, mode='r+b') as f:
    contents = f.readlines()
    contents[0] = contents[0][:-2] + b',selection\r\n'
    f.seek(0,0)
    f.writelines(contents)
