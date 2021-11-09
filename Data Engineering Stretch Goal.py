import arcgis
import pandas as pd
import os
import arcpy

data_df.head()

# Perform a query on the dataframe using the loc function and the necessary field name.
data_df.loc[data_df['candidatevotes'].isnull()] 

# Determine how many rows are in the table
rowcount = data_df.shape[0]

# Determine how many rows have null candidatevotes 
null_fips_rowcount = data_df.loc[data_df['candidatevotes'].isnull()].shape[0]

# Use a print statement to report this information
print("There were "+str(null_fips_rowcount)+" records with null 'candidatevotes' values in the data.\nThis amounts to " +str(percentage_null_fips)+"% of the available data.")

# Use the notnull function and the loc function to create a new dataframe without null 'candidatevotes' records
data_df = data_df.loc[data_df['candidatevotes'].notnull()]

# Get the first five records of the table
data_df.head()

# Validate NO null 'candidatevotes' records
data_df.loc[data_df['candidatevotes'].isnull()] 

# import system modules
import arcpy

# set the current workspace
arcpy.env.workspace = "C:\JianingHe\Learning Materials\ESRI Spatial Data Science\EsriTraining\DataEngineering_and_Visualization\DataEngineering_and_Visualization.gdb"|


# Set layer to apply symbology to 
inputLayer = "CountyElections2016Enrich"

# Set Layer that output symbology will be based on
symbologyLayer = "default.lyrx"

# Apply the symbology from the symbology layer to the input layer
arcpy.ApplySymbologyFromLayer_management(inputLayer, symbologyLayer)


