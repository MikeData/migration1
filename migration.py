
# coding: utf-8

# In[13]:



from databaker.framework import *


# In[14]:


import pandas as pd

import sys
inputFile = sys.argv[1] #"underlyingdatasheet4.01ipscitizenshipgroupbysexbyagebycountryoflastornextresidence2016.xls"
xl = pd.ExcelFile(inputFile)
sheets = xl.sheet_names


"""
Use databaker to amatch up column index and readable column label
then shift to pandas and incorporate the data
"""
tabs = loadxlstabs(inputFile)
allDataFrames = []

# Get the year from the filename
year = inputFile.split(".xls")[0][-4:]
print(year)

for tab in tabs[-1:]:
    
    rowVars = tab.filter(contains_string("Software Readable Row Label")).shift(1,2)
    rowVars = rowVars.expand(RIGHT).is_not_blank().is_not_whitespace()
    
    rowVarDict = {}
    for r in rowVars:
        rowVarDict.update({int(r.x):r.value})
        skipUntil = r.y
        
    # Use databker to find the end of the sheets
    sheetEnds = tab.filter(contains_string("Source: Office for National Statistics"))
    for sh in sheetEnds:
        lastrow = sh.y -3
    
    
    # Now load the sheet as a dataframe, skipping down to the obs
    for i in range(0, len(sheets)):
        if tab.name == sheets[i]:
            loadSheet = sheets[i]
    
    # Load, skim off the header rows, and replace unwanted column names with _integers (_1, _2 etc)
    # Replace Wanted column names with appropriate databakered rowVar
    oldDf = xl.parse(loadSheet)
    oldDf = oldDf[skipUntil-1:lastrow]
    
    toDelete = []
    newHeaders = []
    for i in range(1, len(oldDf.columns.values)+1):
        if i in rowVarDict.keys():
            newHeaders.append(rowVarDict[i])
        else:
            newHeaders.append("_" + str(i))
            toDelete.append("_" + str(i))
    
    oldDf.columns = newHeaders
    
    # Delete hlding columns _1, _2 etc
    for delMe in toDelete:
        oldDf = oldDf.drop(delMe, axis=1)
        
    oldDf["Time"] = year
    
    allDataFrames.append(oldDf)
    
sourceDf = pd.concat(allDataFrames)
sourceDf[:20]


# In[15]:



"""
Flatten Everything
"""
notObsColumns = ["RESC All EST","Time"]
obsColumns = [x for x in sourceDf.columns.values if x not in notObsColumns]


flatFrames = []
for i in range(0, len(obsColumns)-1, 2):
    
    newDf = pd.DataFrame()
    
    newDf["V4_2"] = sourceDf[obsColumns[i]]
    newDf["Data_Marking"] = "" # for later
    newDf["CI"] = sourceDf[obsColumns[i+1]]
    
    newDf["Time_codelist"] = "Year"
    newDf["Time"] = sourceDf["Time"]
    
    newDf["Geography"] = "United Kingdom"
    newDf["Geography_codelist"] = "K02000001"
    
    newDf["rowVars"] = oldDf["RESC All EST"]
    newDf["colVars"] = obsColumns[i]
    
    flatFrames.append(newDf)
    
flattenedDf = pd.concat(flatFrames)

flattenedDf[-5:]


# In[16]:



"""
Splitting out the row and col vars
"""

def codeListify(cell):
    
    cell = cell.replace(" ", "-")
    cell = cell.lower()
    return cell

    
# We have 4 comma seperated dimension items in rowVars
# Make some columns to put them in
flattenedDf["Flow"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[0].strip().title())
flattenedDf["Flow_codelist"] = flattenedDf["Flow"].apply(codeListify)

flattenedDf["Citizenship Group"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[1][4:].strip())
flattenedDf["Citizenship Group_codelist"] = flattenedDf["Citizenship Group"].apply(codeListify)

flattenedDf["Sex"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[2].strip())
flattenedDf["Sex_codelist"] = flattenedDf["Sex"].apply(codeListify)

# Temp Column
flattenedDf["AGEGROUP"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[3].strip()[:4])

flattenedDf["Age"] = flattenedDf["rowVars"].astype(str).map(lambda x: x.split(",")[3].strip()[3:].strip())
flattenedDf["Age_codelist"] = flattenedDf["Age"].apply(codeListify)

"""
Do the same for col vars
"""

flattenedDf["Country"] = flattenedDf["colVars"].astype(str).map(lambda x: x.split(" ")[1].strip().title())
flattenedDf["Country_codelist"] = flattenedDf["Country"].apply(codeListify)
 
# delete
for col in ["rowVars","colVars"]:
    flattenedDf = flattenedDf.drop(col, axis=1)

    
flattenedDf[-5:]


# In[17]:


"""
Move over data markings
"""

flattenedDf["Data_Marking"][flattenedDf["V4_2"] == "."] = '.'
flattenedDf["V4_2"][flattenedDf["V4_2"] == "."] = ''

flattenedDf[-5:]      


# In[18]:



"""
Reorder
"""

correctOrder = ['V4_2',
                'Data_Marking',
                'CI',
                'Time_codelist', 
                'Time', 'Geography', 
                'Geography_codelist',
                'Flow_codelist', 
                'Flow',
                'Citizenship Group_codelist',
                'Citizenship Group',
                'Sex_codelist',
                'Sex',
                'Age_codelist', 
                'Age',
                'Country_codelist',
                'Country', 
                'AGEGROUP']

orderedDataFrame = pd.DataFrame()

for col in correctOrder:
    orderedDataFrame[col] = flattenedDf[col]
    
orderedDataFrame[-5:]


# In[19]:


orderedDataFrame["AGEGROUP"].unique()


# In[20]:



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

