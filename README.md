# migration1
first go at migration.


### Usage

Clone this repo and download all the relevent (4.01) migration .xls files into its directory, then run either convertAll.sh (if you're on windows put the same commands into a batch file).

note. On MAC you'll need to `chmod +x convertAll.sh` first.

You can add or subtract years from the CSV to be outputted by changing this file. It's pretty self explanatory.


### Hierarchy

The hierarchy CSV created the groupings and was generated using information in the spreadsheet internationalmigrationtableofcontents.xls (linked to from the contents sheet of the data excels) as well as the groupings shown within the data.

### Age Groups

There are three age groupings present in the data (shown below). We can't differentiate with
a dimension without introducing tons of sparsity.

The script generates all three but for now we're just using AGQ (details of the groupings are given below).


### Age Groupings

Quinary age groups	(AGQ)
0 - 4
	5 - 9
	10 - 14
	15 - 19
	20 - 24
	25 - 29
	30 - 34
	35 - 39
	40 - 44
	45 - 49
	50 - 54
	55 - 59
	60 - 64
	65 - 69
	70 - 74
	75 - 79
	80 - 84
	85 - 89
	90 and over


Alternative age groups 1	 (AG1)
0 - 16
	17 - 18
	19 - 21
	22 - 59
	60 - 64
	65 and over


Alternative age groups 2	(AG2)
0 - 14
	15 - 24
	25 - 44
	45 - 59
	60 - 64
	65 and over
