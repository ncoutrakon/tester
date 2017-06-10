# https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-VII


import pandas as pd
import numpy as np

def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a
    benchmark of zero (i.e. no risk-free rate information).

    Parameters:
    returns - A pandas Series representing period percentage returns.
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)


def create_drawdowns(equity_curve):
    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the
    pnl_returns is a pandas Series.

    Parameters:
    pnl - A pandas Series representing period percentage returns.

    Returns:
    drawdown, duration - Highest peak-to-trough drawdown and duration.
    """

    # Calculate the cumulative returns curve
    # and set up the High Water Mark
    # Then create the drawdown and duration series
    hwm = [0]
    eq_idx = equity_curve.index
    drawdown = pd.Series(index = eq_idx)
    duration = pd.Series(index = eq_idx)

    # Loop over the index range
    for t in range(1, len(eq_idx)):
        cur_hwm = max(hwm[t-1], equity_curve[t])
        hwm.append(cur_hwm)
        drawdown[t]= hwm[t] - equity_curve[t]
        duration[t]= 0 if drawdown[t] == 0 else duration[t-1] + 1
    return drawdown.max(), duration.max()


def clean_vp(vp):
    px = sorted(list(k for k, v in vp.items()), reverse = True)
    vol = list(vp[p] for p in px)
    df = pd.DataFrame([px, vol]).T
    return df


def clean_vb(vb):
    bars = list([p[0], p[1], p[2], p[3], p[4], (p[1] < p[4])] for p in vb)
    bars = pd.DataFrame(bars).T
    bars.index = ["Time", "Open", "High", "Low", "Close", "Up"]
    return bars


def clean_range(range_bars):
    dates = list(d[0] for d in range_bars)
    ranges = list(d[1] for d in range_bars)
    ranges = list(d.items() for d in ranges)
    ranges = list(sorted(d, key=lambda x: x[0], reverse = True) for d in ranges)
    ranges = pd.DataFrame(ranges).T
    ranges.columns = dates

    return ranges

