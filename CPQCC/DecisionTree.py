#!/bin/python

import pydotplus
import pandas as pd

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import export_graphviz
from sklearn.externals.six import StringIO


def get_data():
    df = pd.read_csv('CPQCC_Data_DT.csv')

    # Clean this data
    drop_columns = (
        'ACETAMIN DCCDONE GASPH DRLMA CAFFEINE VITAMINA ACETAMIN PROBIOTICS NEWOX28 DELMOD ANCMHYP ANCMDIA ANCMAMAGSULF')
    drop_columns = drop_columns.split()
    df = df.drop(drop_columns, axis=1)
    df = df.dropna()

    return df


def classify(df):
    # Split the data into testing and training columns
    train, test = train_test_split(df)

    train_x = train.drop('OX36', axis=1)
    train_y = train[['OX36']].values.ravel()
    test_x = test.drop('OX36', axis=1)
    test_y = test[['OX36']].values.ravel()

    clf = DecisionTreeClassifier(max_depth=5)
    clf.fit(train_x, train_y)

    acc = accuracy_score(
        test_y, clf.predict(test_x))

    print(len(df), acc)
    return clf


def plot_classifier(df, clf):
    dot_data = StringIO()
    export_graphviz(
        clf,
        out_file=dot_data,
        filled=True,
        rounded=True,
        special_characters=True,
        feature_names=df.columns.drop('OX36'),
        class_names=['No BPD', 'BPD'])
    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
    graph.write_png('DecisionTree.png')


dataframe = get_data()
classifier = classify(dataframe)
plot_classifier(dataframe, classifier)
