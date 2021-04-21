#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 16:11:56 2019

@author: sjmoneyboss
"""

import pandas as pd
import statsmodels
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
import datetime
import math
import pandas_datareader.data as web
import datetime as dt
from datetime import datetime
import csv
import numpy as np
from pandas_datareader import data as web
from openpyxl import load_workbook
import matplotlib.pyplot as plt
from matplotlib import style
import xlrd
from matplotlib.pyplot import figure



""" In this program, I will be compiling the 3 different programs: models.py, stationarity.py
and cointegration.py to build a very simplestic pairs trading strategy """

"""Part-1 of the Program: Fetching data from sources and storing it in a CSV file """

def get_price(symbol): #YYYY/MM/DD
    s_year, s_month, s_day = [int(val) for val in input("Enter the Start Date (YYYY-MM-DD): ").split('-')]
    e_year, e_month, e_day = [int(val) for val in input("Enter the End Date (YYYY-MM-DD): ").split('-')]
    start = datetime(s_year, s_month, s_day)
    end = datetime(e_year, e_month, e_day)
    df = web.DataReader(symbol, 'yahoo', start, end)
    filename = symbol + ".csv"
    df.to_csv(filename)
    #print(df.tail())
    #df['Close'].plot(grid=True, figsize=(9,6))
    #plt.ylabel("Price")


symbol_1 = input("Enter the first Symbol/Ticker: ")
get_price(symbol_1)
symbol_2 = input("Enter the second Symbol/Ticker: ")
get_price(symbol_2)

print()
print()
print("CSV files for the symols requested have been created!")
print()

"""Part-2 of the Program: Fetching the CSV file and storing them in Pandas DataFrames """

filename1 = input("Enter the first filename (eg. SPY.csv): ")
filename2 = input("Enter the second filename (eg. DIA.csv): ")

df1 = pd.read_csv(filename1)
df2 = pd.read_csv(filename2)

data1 = df1['Close']
data1.name = filename1.split('.')[0]
data2 = df2['Close']
data2.name = filename2.split('.')[0]



""" Part=3 of the Program: Checking stationarity for the time series data1 and data2 """

""" Now below we will run Augmented Dickey Fuller test on the series and check it's stationarity"""

print()

result1 = adfuller(data1)
print("Result from the ADF Test (for 1st Security): ")
print()
print('ADF Statistic: %f' % result1[0])
print('p-value: %f' % result1[1])
print('Critical Values:')
for key, value in result1[4].items():
	print('\t%s: %.3f' % (key, value))

critical_values = list(result1[4].values())
print()
result2 = adfuller(data2)
print("Result from the ADF Test (for 2nd Security): ")
print()
print('ADF Statistic: %f' % result2[0])
print('p-value: %f' % result2[1])
print('Critical Values:')
for key, value in result2[4].items():
	print('\t%s: %.3f' % (key, value))

critical_values = list(result2[4].values())
print()

""" Adding some code on half life """

def half_life(data):
    data_lag = np.roll(data,1)
    data_lag[0] = 0
    data_ret = data - data_lag
    data_ret[0] = 0

    #adds intercept terms to X variable for regression
    data_lag2 = sm.add_constant(data_lag)

    model = sm.OLS(data_ret,data_lag2) #OLS = ordinary least square, for a regression fit
    res = model.fit()

    halflife = -(math.log(2))/res.params[1]

    print("Half Life for ",data.name, ": ", halflife)

half_life(data1)
half_life(data2)

print()

def hurst(ts):
    """Returns the Hurst Exponent of the time series vector ts"""
    # Create the range of lag values
    lags = range(2, 100)

    # Calculate the array of the variances of the lagged differences
    tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]

    # Use a linear fit to estimate the Hurst Exponent
    poly = np.polyfit(np.log(lags), np.log(tau), 1)

    # Return the Hurst exponent from the polyfit output
    return poly[0] * 2.0

print("Hurst(for the Data Series-1) | Mean reverting if value < 0.5:   %s" % hurst(np.log(data1)))
print("Hurst(for the Data Series-2) | Mean reverting if value < 0.5:   %s" % hurst(np.log(data2)))
print()
#print("Price Chart for the 2 securities: ")

#df1['Close'].plot(grid=True, figsize=(9,6))
#df2['Close'].plot(grid=True, figsize=(9,6))
#plt.ylabel("Price")


""" Part-4: Performing Cointegration of the 2 security pairs """

""" let us write the code to calculate the spread first """

data1 = sm.add_constant(data1)
results = sm.OLS(data2, data1).fit()
data1 = data1[filename1.split('.')[0]] #the column name needs to be there inside the square brackets
b = results.params[filename1.split('.')[0]]

spread = data2 - b * data1

""" The code below will plot the prices for SPY and DIA time series, and the ratio
and the zscore time series"""

def zscore(series):
    return (series - series.mean()) / np.std(series)

zscore_data = zscore(spread)

zscore(spread).plot()
plt.axhline(zscore(spread).mean(), color='black')
plt.axhline(1.0, color='red', linestyle='--')
plt.axhline(-1.0, color='green', linestyle='--')
plt.legend(['Spread z-score', 'Mean', '+1', '-1'])


""" In our case, we have the following Entry Signals:
    - When z-score > 1, short 'data2' and buy 'data1'
    - When z-score < -1, buy 'data2' and short 'data1' """

print("Done")
#Pg-109
