#!/bin/python

import pandas as pd
import numpy as np

import statsmodels.api as sm

from imblearn.over_sampling import SMOTE


def logistic_regression(df, independent_variable, title, oversample=False):
    df = df.dropna()

    X = df.drop(independent_variable, axis=1)
    y = df[[independent_variable]]

    if oversample:
        columns = X.columns
        os = SMOTE(random_state=0)
        os_X, os_y = os.fit_sample(X, y)

        X = pd.DataFrame(data=os_X, columns=columns)
        y = pd.DataFrame(data=os_y, columns=[independent_variable])

    logit = sm.Logit(y, X)
    result = logit.fit()

    conf = result.conf_int()
    conf['OR'] = result.params
    conf.columns = ['2.5%', '97.5%', 'OR']
    final_df = np.exp(conf)

    print('\n', title)
    print(result.summary2())
    print(final_df)

    return final_df


def main():
    # Get dataframe
    df = pd.read_csv('CPQCC_Data.csv')

    # Perform first logistic regression
    log_reg_result_df = logistic_regression(
        df, 'OX36', 'Initial Logistic Regression', False)

    # Perform logistic regression taking into account only significant dependent vars
    log_reg_result_df['SIGNIFICANT'] = log_reg_result_df.apply(
        lambda x: False if x['2.5%'] < 1 < x['97.5%'] else True, axis=1)
    log_reg_result_df = log_reg_result_df.query('SIGNIFICANT == True')

    significant_columns = log_reg_result_df.index.to_list()
    significant_columns.append('OX36')
    new_df = df[significant_columns]

    _ = logistic_regression(new_df, 'OX36', 'Logistic Regression with SIGNIFICANT variables only')


if __name__ == '__main__':
    main()
