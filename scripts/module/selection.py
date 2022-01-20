#!/usr/bin/env python

import csv


def check_selection_exist(file: str):
    with open(file, mode='r', encoding='utf-8-sig') as f:
        csv_reader = csv.DictReader(f)
        header = next(csv_reader)
        if "selection" in header:
            return True
        return False

def check_value_exist(file: str):
    with open(file, mode='r', encoding='utf-8-sig') as f:
        csv_reader = csv.DictReader(f)
        header = next(csv_reader)
        if header['selection']:
            return True
        return False

def append_value(file: str, value: str):
    with open(file, mode='r+b') as f:
        contents = f.readlines()
        contents[1] = contents[1][:-2] + f",{value}\r\n".encode('utf-8')
        f.seek(0,0)
        f.writelines(contents)

def update_value(file: str, value: str):
    with open(file, mode='r+b') as f:
        contents = f.readlines()
        nd_arr = contents[1].split(b',')
        if len(nd_arr) != 14:
            nd_arr[-1] = nd_arr[-1][:-2]
            nd_arr.append(f"{value}\r\n".encode('utf-8'))
        elif len(nd_arr) == 14:
            nd_arr = nd_arr[:-1]
            nd_arr.append(f"{value}\r\n".encode('utf-8'))
        contents[1] = b','.join(nd_arr)
        f.seek(0,0)
        f.writelines(contents)

def get_selection(file: str):
    with open(file, mode='r', encoding='utf-8-sig') as f:
        csv_reader = csv.DictReader(f)
        header = next(csv_reader)
        ranges = []
        for t in header['selection'].split(' '):
            r = t.split('-')
            ranges.append({'Start': float(r[0]), 'End': float(r[1])})
        return ranges

def add_selection_col(file: str):
    with open(file, mode='r+b') as f:
        contents = f.readlines()
        contents[0] = contents[0][:-2] + b',selection\r\n'
        f.seek(0,0)
        f.writelines(contents)
        return []

if __name__ == "__main__":
    # filename = "./file/raw/2021-09-26-18-36_ultium_motion_Dr Tsai_2021.09.26 Dr. Tsai_1.csv"
    filename = "./file/raw/2021-09-26-18-39_ultium_motion_Dr Tsai_2021.09.26 Dr. Tsai_2.csv"
    if not check_selection_exist(filename):
        add_selection_col(filename)
    else:
        get_selection(filename)

    update_value(filename, "the other string")
