import os
import pandas as pd


def remove(df, id_, fname):
    """
    delete prompt from dataframe and save to csv file
    :param df: dataframe
    :param id_: id of prompt
    :param fname: csv file name
    :return: dataframe
    """
    df = df.drop(df[df["id"] == id_].index)
    df.to_csv(fname, index=False)
    return
