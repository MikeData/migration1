# coding: utf-8

from databaker.framework import *
import pandas as pd
import sys


"""
A lot of the top level areas/groupings have been abbreviated in the data.
We'll use this map to switch to the more user friendly descriptions later.
"""
topLevelDict = {
    'All':'All countries of last or next residence',
    'EU':'European Union',
    'EU15':'European Union EU15',
    'EU8':'European Union EU8',
    'EU2':'European Union EU2',
    'EEA':'European Economic Area(EEA)',
    'EFTA':'European Free Trade Association(EFTA)',
    'Non-EU':'Non-EU',
    'CW':'Commonwealth All',
    'Old CW':'Old Commonwealth',
    'New CW':'New Commonwealth',
    'Non-EU and Non-CW':'Non-EU and Non-Commonwealth',
    'Europe inc EU':'Europe including EU',
    'Europe exc EU':'Europe excluding EU',
    'Asia':'Asia',
    'Middle East and Central Asia':'Middle East and Central Asia',
    'East Asia':'East Asia',
    'South Asia':'South Asia',
    'South East Asia':'South East Asia',
    'Rest of World':'Rest of World',
    'North Africa':'North Africa',
    'Sub-Saharan Africa':'Sub-Saharan Africa',
    'North America':'North America',
    'Central and South America':'Central and South America',
    'Oceania':'Oceania',
}

inputFile = sys.argv[1]
xl = pd.ExcelFile(inputFile)
sheets = xl.sheet_names

# Get the year from the filename
year = inputFile.split(".xls")[0][-4:]


# Load tabs we want into memory
tabs = loadxlstabs(inputFile)
tabs = tabs[1:] # get rid of contents
if "Datasheet 4.01A" not in [x.name for x in tabs]:
    raise ValueError("Aborting. No tab named 'Datasheet 4.01A' found.") # without this, it wont work. Better to know.


finalFramesList = []
for tab in tabs:

    rowVars = tab.filter(contains_string("Software Readable Row Label")).shift(DOWN).shift(DOWN)
    rowVars = rowVars.expand(RIGHT).is_not_blank().is_not_whitespace()

    rowVarDict = {}
    for r in rowVars:
        rowVarDict.update({int(r.x):r.value})
        skipUntil = r.y

    # Use databker to find the end of the sheets
    # need to iterate bag of one cell, as bag object can't be indexed
    sheetEnds = tab.filter(contains_string("Source: Office for National Statistics"))
    assert len(sheetEnds) == 1, "Aborting. Finding more than one footer. Expecting 1 x 'Source: Office for National Statistics', tab: " + tab.name
    for sh in sheetEnds:
        lastrow = sh.y -3


    # Now load the sheet as a dataframe
    for i in range(0, len(sheets)):
        if tab.name == sheets[i]:
            loadSheet = sheets[i]

    # Parse, but skim off the header and footer
    sourceDf = xl.parse(loadSheet)
    sourceDf = sourceDf[skipUntil:lastrow]


    toDelete = []
    newHeaders = []
    # Replace Wanted column names with appropriate databakered rowVar
    for i in range(0, len(sourceDf.columns.values)):
        if i in rowVarDict.keys():
            newHeaders.append(rowVarDict[i])
        else:
            # Else add to delete list (delete while iterating mangles the processing order)
            newHeaders.append("_" + str(i))
            toDelete.append("_" + str(i))

    sourceDf.columns = newHeaders

    # Delete hlding columns _1, _2 etc
    for delMe in toDelete:
        sourceDf = sourceDf.drop(delMe, axis=1)

    sourceDf["Time"] = year

    sourceDf.to_csv("sample.csv", index=False)


    """
    Flatten Everything
    """

    flatFrames = []
    for i in range(0, len(sourceDf.columns.values)):

        if " EST" in sourceDf.columns.values[i]:

            newDf = pd.DataFrame()

            newDf["V4_2"] = sourceDf[sourceDf.columns.values[i]]
            newDf["Data_Marking"] = "" # for later
            newDf["CI"] = sourceDf[sourceDf.columns.values[i+1]]

            newDf["calendar-years_codelist"] = "Year"
            newDf["Time"] = sourceDf["Time"]

            newDf["uk-only"] = "K02000001"
            newDf["geography"] = "United Kingdom"

            newDf["rowVars"] = sourceDf["Row Label"]
            newDf["colVars"] = sourceDf.columns.values[i]

            flatFrames.append(newDf)

    flatFramesList = pd.concat(flatFrames)
    finalFramesList.append(flatFramesList)


flattenedDf = pd.concat(finalFramesList)
flattenedDf.fillna("", inplace=True)


"""
Splitting out the row and col vars
"""

def codeListify(cell):
    cell = cell.replace(" / ", " ")
    cell = cell.replace(" ", "-")
    cell = cell.lower()
    return cell


# We have 4 comma seperated dimension items in rowVars
# Make some columns to put them in
flattenedDf["flow"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[0].strip().title())
flattenedDf["migration-flow_codelist"] = flattenedDf["flow"].apply(codeListify)

flattenedDf["citizenshipgroup"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[1][4:].strip())
flattenedDf["migration-citizenship-group_codelist"] = flattenedDf["citizenshipgroup"].apply(codeListify)

flattenedDf["sex"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[2].strip().replace("Persons", "All"))
flattenedDf["migration-sex_codelist"] = flattenedDf["sex"].apply(codeListify)

# Temp Column
flattenedDf["AGEGROUP"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[3].strip()[:4])

flattenedDf["age"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[3].strip()[3:].strip())
flattenedDf["migration-age_codelist"] = flattenedDf["age"].apply(codeListify)



"""
Do the same for col vars
"""
def cleanCountry(country):
    country = " ".join(country.split(" ")[1:-1]).strip()
    removeAll = ["(", ")", ","]
    for rm in removeAll:
        country = country.replace(rm, "")
    return country


# Add basic country data
flattenedDf["country"] = flattenedDf["colVars"].astype(str).apply(cleanCountry)

# Style if into codes
flattenedDf["migration-country_codelist"] = flattenedDf["country"].apply(codeListify)

# Now apply more verbose/use-friendly labels
for key in topLevelDict.keys():
    flattenedDf["country"] = flattenedDf["country"].map(lambda x: x.replace(key,topLevelDict[key]))


# delete
for col in ["rowVars","colVars"]:
    flattenedDf = flattenedDf.drop(col, axis=1)



"""
Move over data markings
"""

flattenedDf["Data_Marking"][flattenedDf["V4_2"] == "."] = '.'
flattenedDf["V4_2"][flattenedDf["V4_2"] == "."] = ''

"""
Reorder
"""

correctOrder = ['V4_2',
                'Data_Marking',
                'CI',
                'calendar-years_codelist',
                'Time', 'uk-only',
                'geography',
                'migration-flow_codelist',
                'flow',
                'migration-citizenship-group_codelist',
                'citizenshipgroup',
                'migration-sex_codelist',
                'sex',
                'migration-age_codelist',
                'age',
                'migration-country_codelist',
                'country',
                'AGEGROUP']

orderedDataFrame = pd.DataFrame()

for col in correctOrder:
    orderedDataFrame[col] = flattenedDf[col]


# Splitting up
# have to use != as all three outputs want the "Age" AgeGroup (the "all" dimension for age)

# AGQ
frame = pd.DataFrame()
frame = orderedDataFrame[orderedDataFrame["AGEGROUP"] != "AG2 "]
frame = frame[frame["AGEGROUP"] != "AG1 "]
frame = frame.drop("AGEGROUP", axis=1)
frame.to_csv("AGQ_citizenshipgroupbysexbyagebycountryoflastornextresidence_" + year + ".csv", index=False)

# AG1
frame = pd.DataFrame()
frame = orderedDataFrame[orderedDataFrame["AGEGROUP"] != "AGQ "]
frame = frame[frame["AGEGROUP"] != "AG1 "]
frame = frame.drop("AGEGROUP", axis=1)
frame.to_csv("AG2_citizenshipgroupbysexbyagebycountryoflastornextresidence_" + year + ".csv", index=False)

# AG2
frame = pd.DataFrame()
frame = orderedDataFrame[orderedDataFrame["AGEGROUP"] != "AG2 "]
frame = frame[frame["AGEGROUP"] != "AGQ "]
frame = frame.drop("AGEGROUP", axis=1)
frame.to_csv("AG1_citizenshipgroupbysexbyagebycountryoflastornextresidence_" + year + ".csv", index=False)
