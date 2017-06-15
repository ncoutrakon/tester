# https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-VII


import pandas as pd
import numpy as np
import copy as cp

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


def clean_trade_activity(ta):
    # cleans up portfolio.trade_activity[sym] for output
    # returns pandas DataFrame
    ta_copy = ta[:]
    ta_copy[0].extend(["Runup", "Drawdown", "PnL", "Cum PnL"])

    # add runup and drawdowns for long and shorts
    list(t.extend([t[8] - t[4], t[9] - t[4]]) for t in ta_copy[1:] if t[1] == "LONG")
    list(t.extend([t[4] - t[9], t[4] - t[8]]) for t in ta_copy[1:] if t[1] == "SHORT")

    pnl = list(np.power(-1, t[1] == "LONG") * (t[4] - t[5]) for t in ta_copy[1:])
    cum_pnl = np.cumsum(pnl)

    # add pnl and cum_pnl to trade activity lists
    list(t.extend([p, c]) for t, p, c in zip(ta_copy[1:], pnl, cum_pnl))

    ta_copy = pd.DataFrame(ta_copy[1:], columns = ta_copy[0])
    return ta_copy

