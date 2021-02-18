# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 12:16:05 2020

@author: Vincent Roye
"""

# Import pandas 
import pandas as pd


def get_brrb():
    return pd.read_csv("../data/recommendations/BRRB.csv")


def get_brsa():
    return pd.read_csv("../data/recommendations/BRSA.csv")


def get_br():
    return pd.concat([get_brrb(), get_brsa()], ignore_index=True)


def get_qqq():
    return pd.read_csv("../data/daily/QQQ.csv")
