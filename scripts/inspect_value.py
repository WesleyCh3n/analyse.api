
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from pathlib import Path
from tqdm import tqdm

from module.cycle import createGaitCycleList
from module.preprocess import selectIndex
from module.preprocess import createSelectDF
from module.preprocess import convertMilliGToSI
from module.preprocess import separateSupportTime

# file = '../file/raw/v3.18.10-en-sample.csv'

paths = list(Path('../file/raw').iterdir())
dgs = []

for file in tqdm(paths):
    raw_data = pd.read_csv(file, skiprows=np.array([0,1,2]), low_memory=False)
    sel_dict = selectIndex(raw_data.columns)
    df = createSelectDF(raw_data, sel_dict)
    df = convertMilliGToSI(df)
    df = separateSupportTime(df)
    list_gait, df_gait = createGaitCycleList(df, 'double_support')

    df['step'] = np.nan
    for i in range(len(df_gait)-1):
        start, end = df_gait.start[i], df_gait.start[i+1]
        df.loc[(start <= df['time']) & (df['time'] < end), ['step']] = i

    df = df.dropna()
    dg = df.groupby(['step'])['Pelvis_A_X'].agg(np.ptp).to_frame().reset_index()
    dg['file'] = file.stem
    dgs.append(dg)


dgs_all = pd.concat(dgs)
sns.scatterplot(data=dgs_all, x='step', y='Pelvis_A_X', hue='file')
plt.show()
