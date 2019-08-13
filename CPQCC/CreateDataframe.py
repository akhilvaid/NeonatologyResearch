#!/bin/python

import os
import sqlite3

import pandas as pd
import numpy as np

# import seaborn as sns
# sns.set()

class Criteria:
    # TODO
    # The following have been disincluded - but this requires verification
    # HISP MATRACE

    # The following variables have additional information attached to them
    # See if inclusion is warranted
    # MULT: NBIRTHS

    # Spaces are necessary at the end of each line
    # or the first/last word get picked up as one
    keep_columns = (
        'BWGT GAWEEKS GADAYS SEX '
        'LOCATE DAYADMISS MAGE PCARE GROUPBSTREP ASTER '
        'SPLABOR MULT DELMOD '
        'ANCMHYP ANCMOINF ANCMDIA ANCMAMAGSULF ANCMCES '
        'ANCFIUGR ANCFDIS ANCFANO ANCOLABOR ANCOPREPROM ANCOPREROM ANCOPROM '
        'ANCOMAL ANCOBLEED DCCDONE DCCCORDMILK DCCBREATH AP1 PA GASPH GASBD '
        'DROX DRCPAP DRBM DRET DREP DRCC DRNIPPV DRLMA SURFX SURF1DHR SURF1DMIN '
        'OXY VENT HFV HFNC NIMV CPAP CPAPES DURVENT VENTDAYS '
        'RDS PNTX MECONIUM CAFFEINE VITAMINA NITRICO ECMO POSTSTER POSTERCLD OX36 EBSEPS '
        'LBPATH CNEGSTAPH FUNGAL VIRAL PDA INDOMETH ACETAMIN PROBIOTICS '
        'NEC GIPERF ISTAGE VEGF SHUNT OTHHEM PVL SEIZURE HIE CMAL '
        'BILILEVEL ')
    keep_columns = keep_columns.split()

    # Get saner values per column
    replacement_dict = {
        'SEX': {9: np.nan},
        'DAYADMISS': {77: 1},
        'PCARE': {9: 0},
        'GROUPBSTREP': {7: 0, 9: 0},
        'ASTER': {9: 0},
        'SPLABOR': {9: 0},
        'MULT': {9: 0},
        'DELMOD': {2:1, 9: 1},
        'ANCMHYP': {9: 0},
        'ANCMOINF': {9: 0},
        'ANCMAMAGSULF': {9: 0},
        'ANCMCES': {9: 0},
        'ANCFIUGR': {9: 0},
        'ANCFDIS': {9: 0},
        'ANCFANO': {9: 0},
        'ANCOLABOR': {9: 0},
        'ANCOPREPROM': {9: 0},
        'ANCOPREROM': {7: 0, 9: 0},
        'ANCOPROM': {7: 0, 9: 0},
        'ANCOMAL': {9: 0},
        'ANCOBLEED': {9: 0},
        'DCCDONE': {9: 0},
        'DCCCORDMILK': {9: 0},
        'DCCBREATH': {9: 0},
        'GASPH': {77.7: np.nan, 99.9: np.nan},
        'GASBD': {77.7: np.nan, 88.8: np.nan, 99.9: np.nan},
        'DROX': {9: 0},
        'DRCPAP': {9: 0},
        'DRBM': {9: 0},
        'DREP': {9: 0},
        'DRET': {9: 0},
        'DRCC': {9: 0},
        'DRNIPPV': {9: 0},
        'DRLMA': {9: 0},
        'SURFX': {9: 0},
        'SURF1DHR': {7777: np.nan, 9999: np.nan},
        'SURF1DMIN': {7777: np.nan, 9999: np.nan},
        'OXY': {7: 0, 9: 0},
        'VENT': {7: 0, 9: 0},
        'HFV': {7: 0, 9: 0},
        'HFNC': {7: 0, 9: 0},
        'NIMV': {2: 1, 7: 0, 9: 0},
        'CPAP': {7: 0, 9: 0},
        'CPAPES': {7: 0, 9: 0},
        'DURVENT': {7: 0, 9: 0},
        'VENTDAYS': {7777: 1, 9999: 0},
        'RDS': {7: 0, 9: 0},
        'PNTX': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'MECONIUM': {7: 0, 9: 0},
        'CAFFEINE': {7: 0, 9: 0},
        'VITAMINA': {7: 0, 9: 0},
        'NITRICO': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'ECMO': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'POSTSTER': {7: 0, 9: 0},
        'OX36': {7: 0, 9: 0, 3: 1, 2: 0},
        'EBSEPS': {2:1, 3:1, 4:1, 7: 0, 9: 0},
        'LBPATH': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'CNEGSTAPH': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'FUNGAL': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'VIRAL': {7: 0, 9: 0},
        'PDA': {7: 0, 9: 0, 2: 1},
        'INDOMETH': {7: 0, 9: 0},
        'ACETAMIN': {7: 0, 9: 0},
        'PROBIOTICS': {7: 0, 9: 0},
        'NEC': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'GIPERF': {7: 0, 9: 0, 11: 1, 12: 1, 13: 1},
        'ISTAGE': {7: np.nan, 9: np.nan},
        'VEGF': {7: 0, 9: 0},
        'SHUNT': {7: 0, 9: 0},
        'OTHHEM': {7: np.nan, 9: np.nan},
        'PVL': {7: np.nan, 9: np.nan},
        'SEIZURE': {7: 0, 9: 0},
        'HIE': {7: 0, 9: 0, 3: 1, 4: 1, 5: 1},
        'CMAL': {9: 0},
        'BILILEVEL': {7: np.nan, 9: np.nan},
    }

    # Replace invalid/missing values in these columns by the mean
    # of the rest of the series
    mean_replacement_dict = {
        'GAWEEKS': 99,
        'GADAYS': 99,
        'MAGE': 99,
    }

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

    # Replace data according to the mean dict
    for i in Criteria.mean_replacement_dict.items():
        replace_variable = i[0]
        replace_value = i[1]

        this_mean = dataframe[replace_variable].replace(replace_value, np.nan).mean()
        dataframe[replace_variable].replace(i[1], this_mean, inplace=True)

    # Special cases that need additional processing
    dataframe['GADAYS'] = dataframe.apply(lambda x: x['GAWEEKS'] * 7 + x['GADAYS'], axis=1)
    # dataframe['CSEC'] = dataframe.apply(lambda x: 1 if x['DELMOD'] == 0 else 0, axis=1)
    # dataframe['AP5'] = dataframe.apply(lambda x: x['AP1'] if x['AP5'] == 99 else x['AP5'], axis=1)
    dataframe['SURFMINS'] = dataframe.apply(lambda x: x['SURF1DHR'] * 60 + x['SURF1DMIN'], axis=1)

    # Drop columns in the dataframe that have more than 50% NaNs
    # which can't be reasonably replaced
    drop_columns = []
    for i in dataframe.columns:
        column_full = dataframe[i].count() / len(dataframe)
        if column_full < 0.5:
            drop_columns.append(i)

    # Drop columns for being summarily unnecessary
    drop_columns.extend(['GAWEEKS', 'SURF1DHR', 'SURF1DMIN'])
    dataframe = dataframe.drop(drop_columns, axis=1)

    # Drop indices which have less than 50% data available
    drop_indices = []
    total_columns = len(dataframe.columns)
    for i in range(len(dataframe)):
        null_perc = dataframe.iloc[i].isnull().sum() / total_columns
        if null_perc > 0.5:
            drop_indices.append(i)
    dataframe = dataframe.drop(drop_indices)

    return dataframe


def correlation_heatmap(dataframe):
    def color_corre(val):
        color = 'black'
        if val > 0.5:
            color = 'green'
        if val < -0.5:
            color = 'red'
        return 'background-color: %s' % color

    s = dataframe.corr().style.applymap(color_corre)
    s.to_excel('Correlation.xlsx')


df = get_data()
df = clean_data(df)
df.to_csv('CPQCC_Data.csv', index=False)
# correlation_heatmap(df)
