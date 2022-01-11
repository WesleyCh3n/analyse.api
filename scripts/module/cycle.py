import numpy as np

def createGaitCycleList(df, dsIndex="double_support"):
    doubleSupportArr = df[dsIndex].values
    mask = (doubleSupportArr[:-1]==False) & (doubleSupportArr[1:]==True)
    doubleSupportStartIndex = np.where(mask)[0] + 1
    gStart = doubleSupportStartIndex[::2] # 2 step one cycle

    # add start and end index for drawing
    dfIndex = np.r_[0, gStart, df.shape[0]-1]
    dfStep = (df
        .loc[dfIndex, 'time']
        .to_frame(name="start")
        .reset_index(drop=True)
    )
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
