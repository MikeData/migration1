
"""
Quick pythons script that renames columns to match what we need/want for loading onto CMD.
At time of writing, this is still being decided. hence seperate script.

If youre reading this at a later date and migration has been published then you can safely move this functionality into migration.py.
"""

import pandas as pd

files = ["AGQcombinedYears.csv", "AG1combinedYears.csv", "AG2combinedYears.csv"]

for f in files:

    replace = {
            "Time_codelist":"calendar-years_codelist",
            "Geography":"uk-only",
    }


    df = pd.read_csv(f)

    lowerCase = False
    lowerCaseFrom = "geography"

    newColumnHeaders = []
    for col in df.columns.values:

        if col in replace:
            col = replace[col]

        if col == lowerCaseFrom:
            lowerCase = True

        if lowerCase:
            col = col.lower().replace(" ", "")

        newColumnHeaders.append(col)

    df.columns = newColumnHeaders
    df.to_csv(f, index=False)
