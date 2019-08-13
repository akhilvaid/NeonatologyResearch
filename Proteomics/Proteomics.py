#!/bin/python

import numpy as np
import pandas as pd


class Criteria:
    vitamin_d_concentrations = '0 250 500 1000'.split()
    columns_to_keep = 'Accession 0_1 0_2 250_1 250_2 500_1 500_2 1000_1 1000_2'.split()
    cutoff_ratio = 1.5


def ratio_classifier(ratio_250, ratio_500, ratio_1000, relationship, dose_dependent=True):
    if relationship == 'increased':
        first_condition = ratio_250 < ratio_500 < ratio_1000
        second_condition = min([ratio_250, ratio_500, ratio_1000]) > Criteria.cutoff_ratio

    elif relationship == 'decreased':
        first_condition = ratio_250 > ratio_500 > ratio_1000
        second_condition = max([ratio_250, ratio_500, ratio_1000]) < 1

    if dose_dependent:
        # All 3 values must be above / below specified cutoffs
        # AND their ratios must change in a dose dependent manner
        return first_condition and second_condition
    else:
        # All 3 values must be above / below specified cutoffs
        return second_condition


def get_data():
    # Just keep the following values for now
    df = pd.read_excel('073117all8.xlsx')
    df = df[Criteria.columns_to_keep]
    return df


def process_data(df):
    # Create columns for averages
    for i in Criteria.vitamin_d_concentrations:
        column_name = f'avg_{i}'
        run_1 = f'{i}_1'
        run_2 = f'{i}_2'
        df[column_name] = df.apply(lambda x: (x[run_1] + x[run_2]) / 2, axis=1)

    # Create columns for ratios across experiment / control runs
    control_column = 'avg_0'
    for i in Criteria.vitamin_d_concentrations[1:]:
        column_name = f'ratio_{i}'
        experiment_column = f'avg_{i}'
        df[column_name] = df.apply(
            lambda x:
            x[experiment_column] / x[control_column] if x[control_column] != 0 else np.nan, axis=1)

    # Create a column to show if concentration of the protein increased across each run
    # And another if ALL the values are above the cutoff
    df['increased'] = df.apply(
        lambda x:
        True if
        ratio_classifier(x['ratio_250'], x['ratio_500'], x['ratio_1000'], 'increased', False)
        else False, axis=1)
    df['inc_over_cutoff'] = df.apply(
        lambda x:
        True if
        ratio_classifier(x['ratio_250'], x['ratio_500'], x['ratio_1000'], 'increased')
        else False, axis=1)

    # Same thing but for decreased
    df['decreased'] = df.apply(
        lambda x:
        True if
        ratio_classifier(x['ratio_250'], x['ratio_500'], x['ratio_1000'], 'decreased', False)
        else False, axis=1)
    df['dec_over_cutoff'] = df.apply(
        lambda x:
        True if
        ratio_classifier(x['ratio_250'], x['ratio_500'], x['ratio_1000'], 'decreased')
        else False, axis=1)

    return df


def colorize(val):
    color = 'black'
    if val != np.inf:
        if val > Criteria.cutoff_ratio:
            color = 'green'
        if val < 1 and val != 0:
            color = 'yellow'
    return 'background-color: %s' % color


dataframe = get_data()
dataframe = process_data(dataframe)

# Colorize ratio columns
ratio_columns = [i for i in dataframe.columns if i.startswith('ratio_')]
s = dataframe.style.applymap(colorize, subset=ratio_columns)
s.to_excel('output.xlsx', index=False)
