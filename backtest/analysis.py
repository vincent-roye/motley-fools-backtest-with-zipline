# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 14:20:51 2020

@author: Vincent Roye
"""

# Import visualization
import matplotlib.pyplot as plt


def draw_plots(perf):
    
    fig = plt.figure(figsize=(12, 12))

    ax = fig.add_subplot(511)
    ax.set_title('Strategy Results')
    ax.semilogy(perf['portfolio_value'], linestyle='-', label='Equity Curve', linewidth=3.0, color="black")
    ax.legend()
    ax.grid(True)

    ax = fig.add_subplot(512)
    ax.plot(perf.CASH, label='Cash', linestyle='-', linewidth=2.0, color="green")
    ax.legend()
    ax.grid(True)

    ax = fig.add_subplot(513)
    ax.semilogy(perf.POSITIONS_VALUE, label='Positions Value', linestyle='-', linewidth=2.0, color="green")
    ax.legend()
    ax.grid(True)

    ax = fig.add_subplot(514)
    ax.plot(perf['returns'], label='Returns', linestyle='-.', linewidth=1.0, color="red")
    ax.legend()
    ax.grid(True) 
    
    ax = fig.add_subplot(515)
    ax.plot(perf.POSITION_COUNT, label='Total Position Count', linestyle='-', linewidth=1.0, color="blue")
    ax.legend()
    ax.grid(True)

    plt.show()