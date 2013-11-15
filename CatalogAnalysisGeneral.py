# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Catalog Analysis

# <codecell>

##We need to import modules that have certain functions necessary to complete the analysis

import pandas as pd
from pandas import DataFrame, Series
from pandas import merge
import numpy as np
import csv

# <headingcell level=5>

# Create some variables which are the files you import, the input will change based on your personal file settings

# <codecell>

#These are your variables that are unique to your file settings
# For the entire analysis...the only thing you need to change are the paths to the files

Currentfile = open('C:/Users/alexisperez/Documents/Stanley Stockroom/UC Berkeley/Current.txt')
Proposedfile = open('C:/Users/alexisperez/Documents/Stanley Stockroom/UC Berkeley/Proposed.txt')
Spendfile= open('C:/Users/alexisperez/Documents/Stanley Stockroom/UC Berkeley/PO.csv')

#These functions will open and read the files that are assigned to your above variables
Current = pd.read_table(Currentfile)
Proposed = pd.read_table(Proposedfile)

Spend = pd.read_csv(Spendfile)

# <codecell>

#In Amount/UOM & UOM the unit of measure might be listed as 1/EA. This won't match up if in the Price catalog it is listed as EA
#Change each UOM column to only the LAST two characters to ensure similarities in format
Spend['Amount/UOM & UOM']= Spend['Amount/UOM & UOM'].astype('str').str[-2:]

Current['Packaging UOM'] = Current['Packaging UOM'].astype('str').str[-2:]

Proposed['Packaging UOM'] = Proposed['Packaging UOM'].astype('str').str[-2:]

# <codecell>

# Create a new Column called PartUOM so we can compare appropriately between all three files
#I experienced an error on occasion with SKU/Catalog #...in some PO files I downloaded, there was no / between SKU and Catalog. Just add the / if this occurs


Spend['PartUOM'] = Spend.apply(lambda x:'%s,%s' % (x['SKU/Catalog #'],x['Amount/UOM & UOM']),axis=1)
Current['PartUOM'] = Current.apply(lambda x:'%s,%s' % (x['Part Number'],x['Packaging UOM']),axis=1)
Proposed['PartUOM'] = Proposed.apply(lambda x:'%s,%s' % (x['Part Number'],x['Packaging UOM']),axis=1)

# <codecell>

# Before merging, we need to make sure that all extraneous symbols are omitted 

Spend['PartUOM'] =Spend['PartUOM'].str.replace("-", "").str.replace(",","").str.replace("/","").str.replace("_","").str.replace(".","")
Current['PartUOM'] = Current['PartUOM'].str.replace("-", "").str.replace(",","").str.replace("/","").str.replace("_","").str.replace(".","")
Proposed['PartUOM'] = Proposed['PartUOM'].str.replace("-", "").str.replace(",","").str.replace("/","").str.replace("_","").str.replace(".","")

# <codecell>

# Merge both of the catalogs
# Create a new dataframe with the specific columns necessary for the analysis

Catalog_Comparison = merge(Current, Proposed, left_on='PartUOM', right_on='PartUOM', how='inner', suffixes=('_x', '_y')) 

comparison = Catalog_Comparison.loc[:,['PartUOM', 'Price_x' , 'Price_y']]

# <codecell>

#Merge the two catalog comparisons with the spend based on PartUOM

Analysis = merge(Spend, comparison, left_on='PartUOM', right_on='PartUOM', how='left') 

# <codecell>

#Extract only the columns that are relevant to the analysis

Catalog_analysis = Analysis.loc[:,[ 'SKU/Catalog #','PartUOM', 'UNSPSC','Manufacturer', 'Quantity', 'Unit Price', 'Extended Price', 'Price_x' , 'Price_y','Item Type']]

# <codecell>

#rename Price_x to Current Price and Price_y to Proposed Price for easier analysis

analysis = Catalog_analysis.rename(columns={'Price_x': 'Current Price', 'Price_y': 'Proposed Price'})


# <codecell>

##If there are any prices removed in the catalogs, the vendors will either put 'Price Removed' in the Proposed catalog under Current 
#   or Proposed Prices

#For the rest of the analysis we don't want 'Price Removed' since this is a string and we can't do operations on the entire column
# We do want to know how many items were removed
##  We can compute that now, and then later change the 'Price Removed' to 0 so we can do calculations
#Here we sum the number of times Price Removed shows up in either of two columns to get the NUMBER OF DELETED ITEMS

removed = analysis['Proposed Price'].str.contains(r'Price Removed').sum()
removed2 = analysis['Current Price'].str.contains(r'Price Removed').sum()

#I put two variables because the vendor could have the Price removed in Current or Proposed Price
print "The number of deleted items is %d and %d" %(removed,removed2)

# <codecell>

#Some Price files may include $ and , in the prices so this will result in the number not being a float
#We use the if analysis...dtype to specify that if the Series is an Object, then we need to remove the $ and , and convert to float.
#Before I didn't specify this and the code omitted all data if I put .str.replace('$') when there was actually no $; Now the new code makes it applicable to any data
# Need to first omit the symbols 
#Then convert to float through .astype

if analysis['Extended Price'].dtype is np.dtype('O'):
 analysis['Extended Price'] = analysis['Extended Price'].str.replace(",","").str.replace("$","")
 analysis['Extended Price']= analysis['Extended Price'].astype('float32')

    
if analysis['Current Price'].dtype is np.dtype('O'):
 analysis['Current Price']= analysis['Current Price'].replace(to_replace= 'Price Removed' , value= 0, inplace=False)
 analysis['Current Price'] = analysis['Current Price'].str.replace(",","").str.replace("$","")
 analysis['Current Price'] = analysis['Current Price'].astype('float32')

    
#In the Proposed Catalog, some prices may be labeled as Price Removed
#Get rid of the Price Removed because these are strings and we want the entire column to consist of floats
#Replace the Price Removed with 0

if analysis['Proposed Price'].dtype is np.dtype('O'):
 
 analysis['Proposed Price']= analysis['Proposed Price'].replace(to_replace= 'Price Removed' , value= 0, inplace=False)
 analysis['Proposed Price'] = analysis['Proposed Price'].str.replace("$", "").str.replace(",","")
    


# <codecell>

##Create the Proposed prices into floats now that 'Price Removed' is a number. Floats allow for computation

analysis['Proposed Price'] = analysis['Proposed Price'].astype('float32')


# <codecell>

#Append computed values at the end of the DataFrame that helps us in the final analysis 
#Compute Ext. Current Price, Proposed Ext. Price, $ Difference and % Difference

analysis['Current Ext. Price'],analysis['Proposed Ext. Price'] = analysis['Quantity']*analysis['Current Price'],analysis['Quantity']*analysis['Proposed Price']
analysis['Current Ext. Price'] = analysis['Current Ext. Price'].astype('float32')
analysis['Proposed Ext. Price'] = analysis['Proposed Ext. Price'].astype('float32')


analysis['$ Difference'] = analysis['Proposed Ext. Price']-analysis['Current Ext. Price']
analysis['% Difference'] = analysis['$ Difference']/analysis['Current Ext. Price']



# <codecell>

# Let's add a validity column


analysis['Valid'] = analysis['Current Price'].notnull() * analysis['Proposed Price'].notnull()

# <codecell>

## Now we can multiply the Extended prices by the Validity column to get the valid spend, valid current and proposed ext. prices

analysis['Valid Spend'] = analysis['Extended Price'] * analysis['Valid']
analysis['Valid Current Ext. Price'] = analysis['Current Ext. Price'] * analysis['Valid']
analysis['Valid Proposed Ext. Price'] = analysis['Proposed Ext. Price'] * analysis['Valid']

# <codecell>

#This locale allows us to convert floats into currency
import locale
locale.setlocale( locale.LC_ALL, '' )


##Sum up the column values to get a total price 
Spend = analysis['Extended Price'].sum()
Valid_Spend = analysis['Valid Spend'].sum()


SUM_Current_Extended_Price = analysis.sum()['Current Ext. Price']
Valid_CurrExt_Price = analysis['Valid Current Ext. Price'].sum()

# We can get the Validity percentage
Validity_percentage = Valid_Spend / Spend
valid_percentage = '{percent:.2%}'.format(percent= Validity_percentage)

SUM_Proposed_Extended_Price = analysis.sum()['Proposed Ext. Price']
Valid_ProposedExt_Price = analysis['Valid Proposed Ext. Price'].sum()

Total_Catalog_Price_Difference = Valid_ProposedExt_Price - Valid_CurrExt_Price
Percent_Increase = Total_Catalog_Price_Difference/Valid_CurrExt_Price
Sum_of_SKUS= analysis['Quantity'].sum()

#set these variables equal to currency so the end result is easier to read

spenddollars = locale.currency(Spend)
valid_spend_dollars = locale.currency(Valid_Spend)
current_price_dollars = locale.currency (Valid_CurrExt_Price)
proposed_price_dollars = locale.currency(Valid_ProposedExt_Price)
price_difference_dollars = locale.currency(Total_Catalog_Price_Difference)

#Now we want the percentage to actually look like a percentage
#Ex. .0007 will simply yield 0 if we don't format it properly

percentage = '{percent:.2%}'.format(percent=Percent_Increase)


#Notice how the variables used are %s not %d. The locale.currency function changes the float into a string.

print "The Total spend is %s and the valid spend is %s" %(spenddollars,valid_spend_dollars)
print "Validity percentage is %s \n" %valid_percentage
print "The Total Quantity of SKUS analyzed is %d \n" %Sum_of_SKUS
print "The Total Valid Current Extended price is %s" %current_price_dollars
print "The Total Proposed Extended price is %s\n\n" %proposed_price_dollars
print "The dollar difference between Total Proposed and Total Current is %s" %price_difference_dollars
print "The percent increase is %s" %percentage


# <codecell>

Count_SKUS = len(analysis['SKU/Catalog #'].unique())

print "The number of SKUS analyzed is %d." %Count_SKUS

# <codecell>


#Let's now get the spend for any products that were removed
#We can create a separate dataframe where the ProposedPrice is 0 AND there exists a Current Price
#First we need to fill the Proposed Prices to 0 if it is empty; Use the fillna() function of the dataframe

# <codecell>


analysis['Proposed Price'] = analysis['Proposed Price'].fillna(0)

# <codecell>

#After filling in the empty spaces with 0 we create a dataframe where the Proposed Price is ONLY zero

proposedprice0=  analysis[analysis['Proposed Price'] == 0]

# <codecell>

#We don't want both Current and Proposed to be zero since that tells us what wasn't bought in the spend
#If there exists a current price and not a proposed then it shows that a price was removed
#Create a dataframe where Proposed Price is ZERO and Current price is some number 

currentnot_zero = proposedprice0[proposedprice0['Current Price'] >0]
Removed_Spend = currentnot_zero['Extended Price'].sum()

#Let's put this value in currency notation
Removed_Spend_Dollars = locale.currency(Removed_Spend)

print "The Removed Spend is %s" %Removed_Spend_Dollars

# <codecell>

##Now if you want to get the top 5 UNSPSC's by spend we have to create a pivot table
#Using a pivot table we will sum up all of the Extended Prices per UNSPSC
#Then we create this table into a new dataframe where we are able to call out the TOP FIVE by spend

from pandas import pivot_table
import numpy as np
 
    
UNSPSC = pivot_table( analysis, values = ['Extended Price', 'Quantity', '$ Difference','Current Ext. Price','Proposed Ext. Price'], rows = ['UNSPSC'], aggfunc = np.sum)

UNSPSC['Percent Increase'] = UNSPSC['$ Difference'] / UNSPSC['Current Ext. Price']
UNSPSC['Percent Increase']= UNSPSC['Percent Increase']*100

# <codecell>

#Want to show the pivot table with the top UNSPSC's by spend
#Use .head() because some pivot tables will be too large to show all of the columns and we only care about the top 5 anyway
UNSPSC.sort("Extended Price", ascending=False).head()

# <codecell>

##Let's do the same but now we want the top Five Manufactuers by Spend
## Proceed with caution when using these figures because there can be multiple names with multiple spends associated to it
## Use Manufacturer.to_csv('C:/..../ManufacturerPivot.csv') to get a copy of this on your computer and see if there are duplicate names

Manufacturer = pivot_table( analysis, values = ['Extended Price', 'Quantity', '$ Difference','Current Ext. Price','Proposed Ext. Price'], rows = 'Manufacturer', aggfunc = np.sum)
Manufacturer['Percent Increase'] = Manufacturer['$ Difference'] / Manufacturer['Current Ext. Price']
Manufacturer['Percent Increase']= Manufacturer['Percent Increase']*100

Manufacturer.sort("Extended Price", ascending=False).head()

# <codecell>

##For the Manufacturer pivot table, there may be more than one manfucturer that is actually the same 
    # ex.   E&K is the same as EK Scientific
    
    #The best way to analyze the top spend by manufacturer is to download this pivot table and analyze it manually to account for same names
   #Save the table with this code
    
Manufacturer.to_csv('C:/Users/alexisperez/Desktop/Manufacturer pivot.csv') 

# <codecell>


