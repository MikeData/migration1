import os
import pandas as pd

files = [f for f in os.listdir('.') if os.path.isfile(f)]

argList = ["AGQ_", "AG1_", "AG2_"]

for arg in argList:
    aList = [x for x in files if arg in x]
    aDfList = []
    for f in aList:

        df = pd.read_csv(f)
        aDfList.append(df)
    pd.concat(aDfList).to_csv(arg + "combinedYears.csv", index=False)
