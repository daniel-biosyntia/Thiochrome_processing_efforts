# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 14:59:29 2022

@author: dan
"""

#%% Packages
import pandas as pd
from scipy.stats import linregress
import numpy as np

#%% Get files and put them in the right format

#Get plate reader file
fn=r'C:\Users\dan\Desktop\R_Stuff\Thiochrome_processing\220303_0304_I_TC'

TC_96_format= pd.read_excel ('%s.xlsx' % fn, 
                             sheet_name="Dil1_01", 
                             skiprows=8, 
                             nrows=8, 
                             index_col=0, 
                             header=1
                             )
#Reshape plate data into a long format 
TC_list=pd.concat(
    [TC_96_format.iloc[:,col] for col in range(0,12)],
    ignore_index=True
    )


#%% Hardcode relevant settings for Thiochrome

#Combining rows and columns - Important, for this to properly match it needs to be ordered by Row
    #Defining rows and cols
rows=["A", "B", "C", "D","E","F","G","H"]
cols=["01","02","03","04","05","06","07","08","09","10","11","12"]
    #Combination Pythonic style because I can
wells_pythonic=[r + c   for c in cols for r in rows]
    #put data into a pandas DataFrame
wells_pythonic=pd.DataFrame(wells_pythonic)
    #Rename Column 
wells_pythonic.rename(columns={0:'Well_Number'}, 
                    inplace=True
                    )



# List with Thiochrome standard concentrations
std_wells=wells_pythonic.iloc[72:,:]
std_conc_uM=[0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 25, 30, 35, 40, 50, 60, 80, 25, 25, 25]
std_wells['Standard_Concentration_uM'] = std_conc_uM



#Build Dataframe
    # Define sample types
sample_type=["sample","standard","QC"]

    #Add wells data
TCH_settings=pd.DataFrame(wells_pythonic)

    #Add sample type info
TCH_settings['Sample_Type']=np.where((TCH_settings.index < 71), sample_type[0], 
                                 np.where((TCH_settings.index < 93), sample_type[1], sample_type[2]))

    #Add Standard Concentration info
TCH_settings=TCH_settings.merge(std_wells, 
                                how='outer', 
                                on="Well_Number")

df_compiled=pd.concat([TCH_settings, TC_list], 
                   axis=1).set_axis(
                       ['Well_Number', 
                        'Sample_Type', 
                        'Standard_Concentration_uM', 
                        'RFUs'],
                       axis=1, 
                       inplace=False)

#%% Data Processing

#Normalized Raw Data
df_normalized = df_compiled #make alterations based on lower values, can be done through function

#define lower  and upper limit of quantification
loqs=[
      1, #LLOQ
      80 #ULOQ
    ]

#subset based on LOQs
df_calibration=df_normalized[(df_normalized["Sample_Type"] == "standard") &
                             (df_normalized['Standard_Concentration_uM'] >= loqs[0]) & 
                             (df_normalized['Standard_Concentration_uM'] <= loqs[1])  
                             
                             ]
#obtain slope, intercept and rvalue from y=mx+b
stats=linregress(
    df_calibration['RFUs'].astype(float),
    df_calibration['Standard_Concentration_uM'].astype(float), 
                 )


#Convertion signal to uM using calibration curve
df_normalized ["Results_uM"] = df_normalized['RFUs']*stats.slope + stats.intercept
#Conversion to mg/L
#Thiamine Molar Mass
Molar_mass_thi=265.33
#Global dilution (if present)
global_dil=1

df_normalized ["Results_mg/L"] =global_dil * df_normalized["Results_uM"]*Molar_mass_thi/1000


#%% Put data back to a 96 format
final_results_list=list(df_normalized ["Results_mg/L"])

final_df_96=pd.DataFrame(rows)
final_df_96.rename(columns={0:' '}, inplace=True)

for x in range(0,12):
    final_df_96[str(x+1)]=final_results_list[x*8:x*8+8]


#Spitting values back to Excel 
    #Define conditions (MOCK dataframes):
final_df_96_1=final_df_96.copy()
final_df_96_1["1"]=1

final_df_96_2=final_df_96.copy()
final_df_96_2["2"]=2

final_df_96_3=final_df_96.copy()
final_df_96_3["3"]=3
    #Define conditions (MOCK Plate Names):
plate_names=["THC mg/L - Plate A", "THC mg/L - Plate B", "THC mg/L - Plate C"]
#Having a list containing dataframes we're gonna loop: list_lists

    #convert df into list of lists
final_df_96_dict1=final_df_96_1.values.tolist()
final_df_96_dict2=final_df_96_2.values.tolist()
final_df_96_dict3=final_df_96_3.values.tolist()

#INPUT
row1=["Something"," "," "," "," "," "," "," "," "," "," "," ", " "]
row2=[' ', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
list_lists=[final_df_96_dict1, final_df_96_dict2, final_df_96_dict3]


#LOOPING to create dataframe
print("I think this will work")