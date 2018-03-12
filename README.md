# migration1
first go at migration.

The files you want are the combinedyears files, there are 3 of them in loadfiles.zip (See below for why there are 3 files). 


### Usage

Clone this repo and download all the relevent (4.01) migration .xls files into its directory, then run either convertAll.sh (MAC) or convertAll.cmd (windows).

note. On MAC you'll need to `chmod +x convertAll.sh` first.

You can add or subtract years from the CSV to be outputted by changing this file. It's pretty self explanatory.



### Age Groups

There are three age groupings present in the data (shown below). We can't differentiate with
a dimension without introducing tons of sparsity.

Didnt want to mix all three in age as it'd look a bit mad so I've extracted as three separate files, so you can always merge them together if you like.

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
  
