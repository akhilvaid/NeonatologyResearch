#!/bin/python

import os
import sqlite3

import pandas as pd
import numpy as np

# import seaborn as sns
# sns.set()

class Criteria:
    # Spaces are necessary at the end of each line
    # or the first/last word get picked up as one

    # All of the following are interventions / controllable variables
    keep_columns = (
        'ASTER DELMOD ANCMHYP ANCMDIA ANCMAMAGSULF DCCDONE GASPH '
        'DROX DRCPAP DRBM DRET DREP DRCC DRNIPPV DRLMA DRSURF SURFX ACOOLING '
        'OXY VENT HFV HFNC NIMV CPAP CPAPES CAFFEINE VITAMINA NITRICO '
        'ECMO POSTSTER NEWOX28 INDOMETH IBUPROFEN ACETAMIN PROBIOTICS EXCHANGE '
        'OX36 ')
    keep_columns = keep_columns.split()

    # Get saner values per column
    replacement_dict = {
        'ASTER': {9: 0},
        'DELMOD': {9: 1},
        'ANCMHYP': {9: 0},
        'ANCMDIA': {9: 0},
        'ANCMAMAGSULF': {9: 0},
        'ANCMDIA': {9: 0},
        'DCCDONE': {9: 0},
        'GASPH': {77.7: np.nan, 99.9: np.nan},
        'DROX': {9: 0},
        'DRCPAP': {9: 0},
        'DRBM': {9: 0},
        'DRET': {9: 0},
        'DREP': {9: 0},
        'DRCC': {9: 0},
        'DRNIPPV': {9: 0},
        'DRLMA': {9: 0},
        'DRSURF': {9: 0},
        'SURFX': {9: 0},
        'ACOOLING': {7: 0, 9: 0},
        'OXY': {7: 0, 9: 0},
        'VENT': {7: 0, 9: 0},
        'HFV': {7: 0, 9: 0},
        'HFNC': {7: 0, 9: 0},
        'NIMV': {2: 1, 7: 0, 9: 0},
        'CPAP': {7: 0, 9: 0},
        'CPAPES': {7: 0, 9: 0},
        'CAFFEINE': {7: 0, 9: 0},
        'VITAMINA': {7: 0, 9: 0},
        'NITRICO': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'ECMO': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'POSTSTER': {7: 0, 9: 0},
        'NEWOX28': {7: 0, 9: 0, 3: 1, 2: 1},  # Check
        'OX36': {7: 0, 9: 0, 3: 1, 2: 0},
        'INDOMETH': {7: 0, 9: 0},
        'IBUPROFEN': {7: 0, 9: 0},
        'ACETAMIN': {7: 0, 9: 0},
        'PROBIOTICS': {7: 0, 9: 0},
        'EXCHANGE': {7: 0, 9: 0},
    }

    # Replace invalid/missing values in these columns by the mean
    # of the rest of the series
    mean_replacement_dict = {}

def get_data():
    path = '/home/akhil/.DriversAndBuilds/WorkingDir/gnosis/Databases/CPQCC/'
    databases = [i for i in os.listdir(path) if i.endswith('.db')]

    root_dataframe = pd.DataFrame()
    for i in databases:
        database = sqlite3.connect(path + i)
        try:
            dataframe = pd.read_sql_query('SELECT * FROM CPQCC', database)
            root_dataframe = root_dataframe.append(
                dataframe, ignore_index=True, sort=False)
        except pd.io.sql.DatabaseError:
            pass

    # Save and load dataframe to get dtypes working
    temporary_file = '_temporary.csv'
    root_dataframe.to_csv(temporary_file)
    root_dataframe = pd.read_csv(temporary_file)
    os.remove(temporary_file)

    return root_dataframe

def clean_data(dataframe):
    dataframe = dataframe[Criteria.keep_columns]

    # Replace data within the dataframe according to the replacement dict
    for i in Criteria.replacement_dict.items():
        replace_variable = i[0]
        replace_values = i[1]

        for j in replace_values.items():
            dataframe[replace_variable].replace(j[0], j[1], inplace=True)

    # Currently this is empty because I'm ify about how DTs use continuous variables
    # Replace data according to the mean dict
    for i in Criteria.mean_replacement_dict.items():
        replace_variable = i[0]
        replace_value = i[1]

        this_mean = dataframe[replace_variable].replace(replace_value, np.nan).mean()
        dataframe[replace_variable].replace(i[1], this_mean, inplace=True)

    # Drop columns in the dataframe that have more than 50% NaNs
    # which can't be reasonably replaced
    drop_columns = []
    for i in dataframe.columns:
        column_full = dataframe[i].count() / len(dataframe)
        if column_full < 0.5:
            drop_columns.append(i)

    # Drop indices which have less than 50% data available
    drop_indices = []
    total_columns = len(dataframe.columns)
    for i in range(len(dataframe)):
        null_perc = dataframe.iloc[i].isnull().sum() / total_columns
        if null_perc > 0.5:
            drop_indices.append(i)
    # dataframe = dataframe.drop(drop_indices)

    return dataframe


df = get_data()
df = clean_data(df)
df.to_csv('CPQCC_Data_DT.csv', index=False)
