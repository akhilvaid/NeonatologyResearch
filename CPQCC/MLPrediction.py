#!/bin/python

import pandas as pd

from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier

from sklearn.preprocessing import scale
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

import statsmodels.api as sm


class Criteria:
    outcome_var = 'OX36'


def get_data():
    # Requisite parameters
    params = [
        'GADAYS', 'SEX', 'ASTER', 'DRCPAP', 'DRBM', 'SURFX',
        'OXY', 'CPAP', 'CMAL', Criteria.outcome_var]

    df = pd.read_csv('CPQCC_Data.csv')
    df = df[params]
    df = df.dropna()

    # Scale all the non-binary parameters
    non_binary_params = ['GADAYS', 'VENTDAYS']
    for i in non_binary_params:
        df[i] = scale(df[i])

    return df


def classify(df):
    # Split the data into testing and training columns
    train, test = train_test_split(df)

    train_x = train.drop(Criteria.outcome_var, axis=1)
    train_y = train[[Criteria.outcome_var]].values.ravel()
    test_x = test.drop(Criteria.outcome_var, axis=1)
    test_y = test[[Criteria.outcome_var]].values.ravel()

    # Test logistic regression as a baseline
    logreg = sm.Logit(train_y, train_x)
    results = logreg.fit(disp=False)
    
    results_array = results.predict(test_x)
    results_array_final = (results_array > 0.8).astype(int)
    
    accuracy = accuracy_score(
        test_y,
        results_array_final)
        
    print('LGR', accuracy * 100)
    
    # Machine learning models
    models = {
        svm.SVC(gamma='scale'): 'SVM',
        KNeighborsClassifier(n_neighbors=5): 'KNN',
        GradientBoostingClassifier(): 'GBM',
        XGBClassifier(): 'XGB'}
    
    for this_model in models:
        this_model.fit(train_x, train_y)
        model_accuracy = accuracy_score(
            test_y,
            this_model.predict(test_x))

        print(models[this_model], model_accuracy * 100)


dataframe = get_data()
classify(dataframe)
