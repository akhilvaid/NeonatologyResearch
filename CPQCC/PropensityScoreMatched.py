#!/bin/python

import subprocess

import pandas as pd
import numpy as np
import seaborn as sns; sns.set()

from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import scale


class Criteria:
    # Logistic regression predicted significant variables:
    # All interventional variables are being dropped from this
    # ['GADAYS', 'SEX', 'ASTER', 'DRCPAP', 'DRBM', 'SURFX', 'OXY',
    # 'HFNC', 'CPAP', 'VENTDAYS', 'NEC', 'CMAL']

    treatment_var = 'CPAP'
    outcome_var = 'OX36'
    covariates = [
        'GADAYS', 'SEX', 'NEC', 'CMAL']

    all_vars = covariates.copy()
    all_vars.extend(
        (outcome_var, treatment_var))


def get_data():
    df = pd.read_csv('CPQCC_Data.csv')

    df = df[Criteria.all_vars]
    df = df.dropna()

    # Scale non binary parameters
    df['GADAYS'] = scale(df['GADAYS'])

    return df


def generate_propensity_scores(df):
    # The treatment variable will be extracted from the dataframe in either case
    # the rest of the dataframe will be used as covariates

    treatment = df[Criteria.treatment_var].values.ravel()
    covariates = df.drop(
        [Criteria.treatment_var, Criteria.outcome_var], axis=1)
    covariates['CONSTANT'] = np.ones(len(covariates))

    gbm = GradientBoostingClassifier()
    gbm.fit(covariates, treatment)

    # Get probabilites
    # The propensity score is the conditional probability of
    # receiving the treatment given the observed covariates
    # Since classes_ for the gbm are 0, 1; we want the 1th column of
    # the probability array

    probabilities_all = gbm.predict_proba(covariates)
    probability_yes = probabilities_all[:, 1]

    df['PROPENSITY'] = probability_yes

    return df.dropna()


def split_dataframe(df):
    # Split into control and treatment groups

    df_c = df[df[Criteria.treatment_var] == 0]
    df_t = df[df[Criteria.treatment_var] == 1]

    return df_c, df_t


def match(df_c, df_t):
    # Match values in the control df
    # with values in the treatment df

    df_c = df_c.reset_index(drop=True)

    nbrs = NearestNeighbors(n_neighbors=1)
    nbrs.fit(df_c.PROPENSITY.values.reshape(-1, 1))
    distances, indices = nbrs.kneighbors(
        df_t.PROPENSITY.values.reshape(-1, 1))
    indices_final = [i[0] for i in indices.tolist()]

    return df_c.iloc[indices_final]


def plot_matching(df_mc, df_t):
    ax = sns.distplot(df_mc.PROPENSITY, label='Control')
    sns.distplot(df_t.PROPENSITY, label='Treatment', ax=ax)
    ax.legend()

    ax.figure.savefig('PropensityScoreDistribution.png', dpi=600)
    subprocess.Popen('xdg-open PropensityScoreDistribution.png', shell=True)


def average_treatment_effect(df_initial, df_mc, df_t):
    # Initial treatment effect
    init_c, init_t = split_dataframe(df_initial)
    outcome_mean_treatment_initial = init_t[Criteria.outcome_var].mean()
    outcome_mean_control_initial = init_c[Criteria.outcome_var].mean()
    delta_init = outcome_mean_treatment_initial - outcome_mean_control_initial

    print(Criteria.treatment_var)

    print(f'{Criteria.outcome_var} in treatment group: {outcome_mean_treatment_initial}')
    print(f'{Criteria.outcome_var} in UNMATCHED control group: {outcome_mean_control_initial}')
    print(f'Final - Initial outcome difference before matching: {delta_init}')
    print()

    # The ATE is the usual final - initial delta
    outcome_mean_treatment = df_t[Criteria.outcome_var].mean()
    outcome_mean_control = df_mc[Criteria.outcome_var].mean()
    delta = outcome_mean_treatment - outcome_mean_control

    print(f'{Criteria.outcome_var} in treatment group: {outcome_mean_treatment}')
    print(f'{Criteria.outcome_var} in MATCHED control group: {outcome_mean_control}')
    print(f'Final - Initial outcome difference after matching: {delta}')


dataframe = get_data()

df_propensities = generate_propensity_scores(dataframe)
df_control, df_treatment = split_dataframe(df_propensities)
df_matched_controls = match(df_control, df_treatment)
plot_matching(df_matched_controls, df_treatment)
average_treatment_effect(dataframe, df_matched_controls, df_treatment)
