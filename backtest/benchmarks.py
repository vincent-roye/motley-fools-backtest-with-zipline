# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 09:29:22 2020

@author: Vincent Roye
"""

# Import pandas 
import pandas as pd 
  

def get_qqq():
    return pd.read_csv("../data/daily/QQQ.csv")


def get_pf_formatted_benchmark(index):
    
    if index =="QQQ":
        
        benchmark = get_qqq()
        
        #Formatting the benchmark for pyfolio
        
        benchmark = benchmark[['date','close']]
        benchmark['close'] = benchmark['close'].pct_change()
        benchmark.dropna(inplace=True)    
        
        benchmark['date'] = pd.to_datetime(benchmark['date'])    
        bechmark = benchmark.set_index('date')
        
        new_benchmark = benchmark.set_index('date').tz_localize('utc')    
        new_benchmark = new_benchmark.iloc[:,0]
        
        return new_benchmark
    
    
get_pf_formatted_benchmark("QQQ")