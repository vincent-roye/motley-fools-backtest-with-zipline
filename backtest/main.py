# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 09:29:22 2020

@author: Vincent Roye
"""

import matplotlib.pyplot as plt

# Import Zipline functions
from pyfolio.timeseries import *
from zipline import run_algorithm
from zipline.api import order, order_value, get_datetime, get_order, symbol, record

# Import visualization
import analysis

import pandas as pd
import pyfolio as pf
import numpy as np

from trades import get_br
from benchmarks import get_pf_formatted_benchmark

# silence warnings
import warnings

warnings.filterwarnings('ignore')

# Parameters

START_DATE = "2005-11-11"
END_DATE = "2020-11-12"

INIT_CAPITAL = 50000
T0_POSITION_SIZE = 2000 # At T0 we will buy for that amount of x different equities
POSITION_SIZE = 550
HOLDING_PERIOD = 180  # days


def buy_order(symbol_str, value_amount, df_index, pos_type, context, data):
    try:
        order_id = order_value(symbol(symbol_str), value_amount)
        order_record = get_order(order_id)

        if order_record is not None:

            # Order the status of the BR -> 1 = Bought. Also register amount and purchase price
            update = [1, order_record.amount, data[symbol(symbol_str)].price]
            context.motley_recom.loc[df_index, ['exec_status', 'amount_bought', 'entry_price']] = update

        else:
            # Order the status of the BR -> 2 = Could not buy
            context.motley_recom['exec_status'][df_index] = 2

    except Exception as e:
        print("Problem buying a position of type : " + str(pos_type))
        print("An exception occurred :" + str(symbol) + " on " + get_datetime().date().strftime('%Y-%m-%d'))
        print(e)


def sell_order(symbol_str, amount, df_index, pos_type, context):
    try:
        order_id = order(symbol(symbol_str), -amount)
        order_record = get_order(order_id)

        if order_record is not None:
            # Order the status of the BR -> 4 = Sold
            context.motley_recom['exec_status'][df_index] = 4

        else:
            # Order the status of the BR -> 5 = Could not sell
            context.motley_recom['exec_status'][df_index] = 5

    except Exception as e:
        print("Problem selling a position of type : " + str(pos_type))
        print("An exception occurred :" + str(symbol) + " on " + get_datetime().date().strftime('%Y-%m-%d'))
        print(e)


def initialize(context):
    context.current_year = START_DATE.split("-")[0]
    context.order_value_br = POSITION_SIZE

    context.initial_stake_bought = False

    # Create dataframe from BR list

    motley_recom = get_br()
    motley_recom['buy_date'] = pd.to_datetime(motley_recom['buy_date'])
    motley_recom.sort_values('buy_date', ascending=False, inplace=True)

    motley_recom['sell_date'] = motley_recom['buy_date'] + pd.DateOffset(days=HOLDING_PERIOD)

    # Order the status of the BR -> 0 = Untouched
    motley_recom['exec_status'] = 0
    motley_recom['pos_type'] = np.nan
    motley_recom['entry_price'] = np.nan
    motley_recom['amount_bought'] = np.nan

    # Create list of equities to buy at T0 with the initial capital

    different_symbols_to_buy_at_t0 = int(round(INIT_CAPITAL / T0_POSITION_SIZE))

    print("Amount of different equities to buy at T0: " + str(different_symbols_to_buy_at_t0))

    init_positions = motley_recom[motley_recom.buy_date <= start_date.date()][:different_symbols_to_buy_at_t0]
    motley_recom.loc[init_positions.index, 'pos_type'] = "init"

    rolling_positions = motley_recom[motley_recom.buy_date > start_date.date()]
    motley_recom.loc[rolling_positions.index, 'pos_type'] = "rolling"

    context.motley_recom = motley_recom[motley_recom['pos_type'].notna()]

    # Load trades after start date

    orders_post_start = motley_recom[motley_recom['buy_date'] > start_date.date()]
    orders_post_start.reset_index(inplace=True, drop=True)

    print("Amount of positions to open after T0:  " + str(len(rolling_positions)))

def handle_data(context, data):
    # global initial_positions

    if context.current_year != get_datetime().date().year:
        context.current_year = get_datetime().date().year
        print("Backtesting year : " + str(context.current_year))

    record(CASH=context.portfolio.cash)
    record(POSITIONS_VALUE=context.portfolio.positions_value)
    record(POSITION_COUNT=len(context.portfolio.positions))

    # Buying initial stake

    if get_datetime().date() >= start_date.date() and not context.initial_stake_bought:

        initial_positions = context.motley_recom[context.motley_recom['pos_type'] == "init"]

        for index, row in initial_positions.iterrows():
            buy_order(row['symbol'], T0_POSITION_SIZE, index, "init", context, data)

        context.initial_stake_bought = True

    # Buying rolling BR equities

    rolling_long_positions = context.motley_recom[
        (context.motley_recom['pos_type'] == "rolling") & (context.motley_recom['exec_status'] == 0)]
    rolling_overdue_long_positions = rolling_long_positions[rolling_long_positions['buy_date'] < get_datetime().date()]

    for index, row in rolling_overdue_long_positions.iterrows():

        # Sell best performing anterior to TO position if insufficient cash for new BR purchase

        if context.portfolio.cash < context.order_value_br:

            motley_recom_init = context.motley_recom[(context.motley_recom['pos_type'] == "init") & (context.motley_recom['exec_status'] == 1)]

            max_increase = -100
            best_performing_stock = ""
            best_performing_stock_amount = 0

            # Find most profitable position
            for index, row in motley_recom_init.iterrows():
                increase = round(((data[symbol(row['symbol'])].price / row['entry_price']) - 1) * 100, 2)
                if increase > max_increase:
                    max_increase = increase
                    best_performing_stock = row['symbol']
                    best_performing_stock_amount = row['amount_bought']

            sell_order(best_performing_stock, best_performing_stock_amount, index, "init", context)

        # Buy new BR
        buy_order(row['symbol'], context.order_value_br, index, "rolling", context, data)

    # Selling rolling BR equities

    rolling_overdue_short_positions = context.motley_recom[
        (context.motley_recom['pos_type'] == "rolling")
        & (context.motley_recom['exec_status'] == 1)
        & (context.motley_recom['sell_date'] < get_datetime().date())
        ]

    if not rolling_overdue_short_positions.empty:

        for index, row in rolling_overdue_short_positions.iterrows():
            sell_order(row["symbol"], row["amount_bought"], index, "rolling", context)


def analyze(context, perf):

    # Custom analysis
    analysis.draw_plots(perf)

    # Pyfolio
    returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf)

    # Custom metrics
    print("Annualized Return: {:.2%}".format(annual_return(returns)))
    print("Max Drawdown: {:.2%}".format(max_drawdown(returns)))
    print("Annualized Standard Deviation: {:.2%} ".format(returns.std()*16))

    pf.create_simple_tear_sheet(returns, benchmark_rets=get_pf_formatted_benchmark("QQQ"))
    plt.show()


# Set start and end date
start_date = pd.Timestamp(START_DATE, tz='utc')
end_date = pd.Timestamp(END_DATE, tz='utc')

# Fire off the backtest
results = run_algorithm(
    start=start_date,
    end=end_date,
    initialize=initialize,
    analyze=analyze,
    handle_data=handle_data,
    capital_base=INIT_CAPITAL,
    data_frequency='daily',
    bundle='us_stocks',
)