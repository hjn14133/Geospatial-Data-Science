import arcgis
import pandas as pd
import os
import arcpy

table_csv_path = r"C:\JianingHe\Learning Materials\ESRI Spatial Data Science\EsriTraining\DataEngineering_and_Visualization\countypres2016.csv"

data_df = pd.read_csv(table_csv_path, dtype={'FIPS': str})

data_df.head()

# Perform a query on the dataframe using the loc function and the necessary field name.
data_df.loc[data_df['FIPS'].isnull()]  # We can use the isnull function built in to Pandas to find the records with null FIPS.

# Determine how many rows are in the table
rowcount = data_df.shape[0]

# Determine how many rows have null FIPS 
null_fips_rowcount = data_df.loc[data_df['FIPS'].isnull()].shape[0]

# Calculate how much of the data this represents as a percentage
percentage_null_fips = round((null_fips_rowcount / rowcount) * 100, 2)

# Use a print statement to report this information
print("There were "+str(null_fips_rowcount)+" records with null FIPS values in the data.\nThis amounts to " +str(percentage_null_fips)+"% of the available data.")

# Use the notnull function and the loc function to create a new dataframe without null FIPS records
data_df = data_df.loc[data_df['FIPS'].notnull()]

# Get the first five records of the table
data_df.head()

# Check how many records have a FIPS value with four characters
trunc_df = data_df.loc[data_df['FIPS'].str.len() == 4]
trunc_data_per = (trunc_df.shape[0] / data_df.shape[0])*100

# Use another print statement (using the f format key) to report this information
print(f"{round(trunc_data_per, 2)}% of data ({trunc_df.shape[0]} rows) has truncated FIPS values.")

# Define a helper function to fix truncated zeros, with one parameter: the value to be processed
def fix_trunc_zeros(val):
    # Use an if statement to check if there are four characters in the string representation of the value
    if len(str(val)) == 4:
        # If this is the case, return the value with an appended "0" in the front
        return "0"+str(val)
    # Otherwise...
    else:
        # Return the value itself
        return str(val)

# Test helper function with truncated value
fix_trunc_zeros(7042)  # You should see an appended zero: "07042"

# Run helper function on the FIPS field using the apply and lambda method 
data_df['FIPS'] = data_df['FIPS'].apply(lambda x: fix_trunc_zeros(x))

# Print information on the operation performed, and show the first few records to confirm it worked
print(f"{round(trunc_data_per, 2)}% of data ({trunc_df.shape[0]} rows) had truncated FIPS IDs corrected.")
data_df.head()

# Set an index using mulitple fields, which "locks" these fields before the table pivots
# Use the built-in groupby function for the FIPS and year fields, which you use to group the data by candidate
# Use unstack to perform the table pivot, which will rotate the table and turn rows into columns
df_out = data_df.set_index(['FIPS', 
                            'year', 
                            'county', 
                            'state', 
                            'state_po', 
                            'office', 
                            data_df.groupby(['FIPS', 'year']).cumcount()+1]).unstack()

# Use the indexes for the columns to set column names (Ex: candidate_1, candidate_2, votes_1, votes_2, etc.)
df_out.columns = df_out.columns.map('{0[0]}_{0[1]}'.format)

# Rename columns 
df_out = df_out.rename(columns={"candidate_1": "candidate_dem",
                                "candidatevotes_1": "votes_dem",
                                "candidate_2": "candidate_gop",
                                "candidatevotes_2": "votes_gop",
                                "totalvotes_1": "votes_total",
                                "state_po": "state_abbrev"
                                })

# Keep only the necessary columns
df_out = df_out[["candidate_dem", "votes_dem",
                 "candidate_gop", "votes_gop",
                 "votes_total"]]

# Remove the multiindex since we no longer need these fields to be "locked" for the pivot
df_out.reset_index(inplace=True)

# Print out the first few records to confirm everything worked
df_out.head()

# Calculate votes that did not choose the Democratic or Republican party
df_out['votes_other'] = df_out['votes_total'] - (df_out['votes_dem'] + df_out['votes_gop'])
df_out.head()

# Calculate voter share attributes
df_out['voter_share_major_party'] = (df_out['votes_dem'] + df_out['votes_gop']) / df_out['votes_total']
df_out['voter_share_dem'] = df_out['votes_dem'] / df_out['votes_total']
df_out['voter_share_gop'] = df_out['votes_gop'] / df_out['votes_total']
df_out['voter_share_other'] = df_out['votes_other'] / df_out['votes_total']

# Calculate raw difference attributes
df_out['rawdiff_dem_vs_gop'] = df_out['votes_dem'] - df_out['votes_gop']
df_out['rawdiff_gop_vs_dem'] = df_out['votes_gop'] - df_out['votes_dem']
df_out['rawdiff_dem_vs_other'] = df_out['votes_dem'] - df_out['votes_other']
df_out['rawdiff_gop_vs_other'] = df_out['votes_gop'] - df_out['votes_other']
df_out['rawdiff_other_vs_dem'] = df_out['votes_other'] - df_out['votes_dem']
df_out['rawdiff_other_vs_gop'] = df_out['votes_other'] - df_out['votes_gop']

# Calculate percent difference attributes
df_out['pctdiff_dem_vs_gop'] = (df_out['votes_dem'] - df_out['votes_gop']) / df_out['votes_total']
df_out['pctdiff_gop_vs_dem'] = (df_out['votes_gop'] - df_out['votes_dem']) / df_out['votes_total']
df_out['pctdiff_dem_vs_other'] = (df_out['votes_dem'] - df_out['votes_other']) / df_out['votes_total']
df_out['pctdiff_gop_vs_other'] = (df_out['votes_gop'] - df_out['votes_other']) / df_out['votes_total']
df_out['pctdiff_other_vs_dem'] = (df_out['votes_other'] - df_out['votes_dem']) / df_out['votes_total']
df_out['pctdiff_other_vs_gop'] = (df_out['votes_other'] - df_out['votes_gop']) / df_out['votes_total']

df_out.head()

# Create variables that represent the ArcGIS Pro project and map
aprx = arcpy.mp.ArcGISProject("CURRENT")
mp = aprx.listMaps('Data Engineering')[0]

# Create a variable that represents the default file geodatabase
fgdb = r"C:\JianingHe\Learning Materials\ESRI Spatial Data Science\EsriTraining\DataEngineering_and_Visualization\DataEngineering_and_Visualization.gdb"
aprx.defaultGeodatabase = fgdb
arcpy.env.workspace = fgdb

# Create a variable that represents the county geometry dataset
counties_fc_name = "Counties_2016_VotingAgePopulation"
counties_fc = os.path.join(fgdb, counties_fc_name)

# Load the dataset into a spatially-enabled dataframe
counties_df = pd.DataFrame.spatial.from_featureclass(counties_fc)
counties_df.head()

# Modify the dataframe to only include the attributes that are needed
counties_df = counties_df[['OBJECTID', 'GEOID', 'GEONAME',
                           'Total_cvap_est',
                           'SHAPE', 'Shape__Area', 'Shape__Length']]
counties_df.head()

# Join the election dataframe with the county geometry dataframe
geo_df = pd.merge(df_out, counties_df, left_on='FIPS', right_on="GEOID", how='left')

# Visualize the merged data
geo_df.head()

# Create a copy of the joined data
data_2016_df = geo_df.copy()
data_2016_df.head()

# Calculate voter turnout attributes
data_2016_df['voter_turnout'] = data_2016_df['votes_total'] / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_majparty'] = (data_2016_df['votes_dem']+data_2016_df['votes_gop']) / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_dem'] = data_2016_df['votes_dem'] / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_gop'] = data_2016_df['votes_gop'] / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_other'] = data_2016_df['votes_other'] / data_2016_df['Total_cvap_est']
data_2016_df.head()

# Check for null values
data_2016_df.loc[data_2016_df['voter_turnout'].isnull()]

# Remove records with no voter turnout value
data_2016_df = data_2016_df.loc[data_2016_df['voter_turnout'].notnull()]

# Run a describe to get the distribution of voter turnout values
data_2016_df['voter_turnout'].describe()

# Perform query for voter turnout above 100%
data_2016_df.loc[data_2016_df['voter_turnout'] > 1]

# Correct each county
data_2016_df.loc[data_2016_df['FIPS'] == "08111", "Total_cvap_est"] = 574
data_2016_df.loc[data_2016_df['FIPS'] == "35021", "Total_cvap_est"] = 562
data_2016_df.loc[data_2016_df['FIPS'] == "48301", "Total_cvap_est"] = 86
data_2016_df.loc[data_2016_df['FIPS'] == "48311", "Total_cvap_est"] = 566

# Recalculate voter turnout fields
data_2016_df['voter_turnout'] = data_2016_df['votes_total'] / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_majparty'] = (data_2016_df['votes_dem']+data_2016_df['votes_gop']) / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_dem'] = data_2016_df['votes_dem'] / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_gop'] = data_2016_df['votes_gop'] / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_other'] = data_2016_df['votes_other'] / data_2016_df['Total_cvap_est']

data_2016_df.loc[data_2016_df['voter_turnout'] > 1]

# Create a feature class for the 2016 presidential election 
out_2016_fc_name = "county_elections_pres_2016"
out_2016_fc = data_2016_df.spatial.to_featureclass(os.path.join(fgdb, out_2016_fc_name))
out_2016_fc

# Perform query for county FIPS 46102
df_out.loc[df_out['FIPS'] == '46102']

df_out.loc[df_out['FIPS'] == '46113']

df_out.loc[df_out['FIPS'] == '46113', 'FIPS'] = "46102"
df_out.loc[df_out['FIPS'] == '46102']

# Join the county geometry data to the updated election data table
geo_df = pd.merge(df_out, counties_df, left_on='FIPS', right_on="GEOID", how='left')

# Create a copy of the data that only includes records from 2016
data_2016_df = geo_df.copy()
data_2016_df.head()

# Correct counties with low population
data_2016_df.loc[data_2016_df['FIPS'] == "08111", "Total_cvap_est"] = 574
data_2016_df.loc[data_2016_df['FIPS'] == "35021", "Total_cvap_est"] = 562
data_2016_df.loc[data_2016_df['FIPS'] == "48301", "Total_cvap_est"] = 86
data_2016_df.loc[data_2016_df['FIPS'] == "48311", "Total_cvap_est"] = 566

# Calculate voter turnout
data_2016_df['voter_turnout'] = data_2016_df['votes_total'] / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_majparty'] = (data_2016_df['votes_dem']+data_2016_df['votes_gop']) / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_dem'] = data_2016_df['votes_dem'] / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_gop'] = data_2016_df['votes_gop'] / data_2016_df['Total_cvap_est']
data_2016_df['voter_turnout_other'] = data_2016_df['votes_other'] / data_2016_df['Total_cvap_est']

# Remove records with no voter turnout value
data_2016_df = data_2016_df.loc[data_2016_df['voter_turnout'].notnull()]

# Create a feature class for the 2016 election and voter turnout data
out_2016_fc_name = "county_elections_pres_2016_final"
out_2016_fc = data_2016_df.spatial.to_featureclass(os.path.join(fgdb, out_2016_fc_name))
