# https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-IV

import datetime
import numpy as np
import pandas as pd
import queue

from abc import ABCMeta, abstractmethod

from event import SignalEvent

class Strategy(object):
    """
    Strategy is an abstract base class providing an interface for
    all subsequent (inherited) strategy handling objects.

    The goal of a (derived) Strategy object is to generate Signal
    objects for particular symbols based on the inputs of Bars
    (OLHCVI) generated by a DataHandler object.

    This is designed to work both with historic and live data as
    the Strategy object is agnostic to the data source,
    since it obtains the bar tuples from a queue object.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        """
        Provides the mechanisms to calculate the list of signals.
        """
        raise NotImplementedError("Should implement calculate_signals()")


class BuyAndHoldStrategy(Strategy):
    """
    This is an extremely simple strategy that goes LONG all of the
    symbols as soon as a bar is received. It will never exit a position.

    It is primarily used as a testing mechanism for the Strategy class
    as well as a benchmark upon which to compare other strategies.
    """

    def __init__(self, bars, events):
        """
        Initialises the buy and hold strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events

        # Once buy & hold signal is given, these are set to True
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to False.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
        return bought

    def calculate_signals(self, event):
        """
        For "Buy and Hold" we generate a single signal per symbol
        and then no additional signals. This means we are
        constantly long the market from the date of strategy
        initialisation.

        Parameters
        event - A MarketEvent object.
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars(s, N=1)
                if bars is not None and bars != []:
                    if self.bought[s] == False:
                        # (Symbol, Datetime, Type = LONG, SHORT or EXIT)
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG', 1)
                        self.events.put(signal)
                        self.bought[s] = True

# will send exit orders if risk or target are met.
# i.e. if last price is risk cents lower than our initial long
# or if last price is greater than target cents
class BracketStrategy(Strategy):
    """
    This is an extremely simple strategy that goes LONG all of the
    symbols as soon as a bar is received. It will never exit a position.

    It is primarily used as a testing mechanism for the Strategy class
    as well as a benchmark upon which to compare other strategies.
    """

    def __init__(self, bars, port, events, risk, target, study):
        """
        Initialises the buy and hold strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.port = port
        self.risk = risk
        self.target = target
        self.study = study
        self.wait_bars = 4

        # Once buy & hold signal is given, these are set to True
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to False.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
        return bought

    def send_exit(self, bars):
        check_risk, check_target = False, False
        if self.port.trade_activity[-1][2] == "LONG":
            check_risk = (self.port.trade_activity[-1][4] - bars[0][5] >= self.risk)
            check_target = (bars[0][5] - self.port.trade_activity[-1][4] >= self.target)
        elif self.port.trade_activity[-1][2] == "SHORT":
            check_target = (self.port.trade_activity[-1][4] - bars[0][5] >= self.target)
            check_risk = (bars[0][5] - self.port.trade_activity[-1][4] >= self.risk)

        return check_risk or check_target

    def wait_period(self, s):
        return len(self.study.data[s]) > self.wait_bars

    def send_entry(self, s):
        study = self.study.data[s]

        go_short = sum(list(v[1] - v[4] > 0 for v in study[-4:-1])) == 3
        go_long = sum(list(v[1] - v[4] < 0 for v in study[-4:-1])) == 3
        if go_long:
            return 1
        if go_short:
            return -1

    def calculate_signals(self, event):
        """
        For "Buy and Hold" we generate a single signal per symbol
        and then no additional signals. This means we are
        constantly long the market from the date of strategy
        initialisation.

        Parameters
        event - A MarketEvent object.
        """

        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars(s, N=1)

                if bars is not None and bars != [] and self.wait_period(s):
                    if not self.bought[s] and self.send_entry(s) == 1:
                        # (Symbol, Datetime, Type = LONG, SHORT or EXIT)
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG', 1)
                        self.events.put(signal)
                        self.bought[s] = True

                    elif not self.bought[s] and self.send_entry(s) == -1:
                        # (Symbol, Datetime, Type = LONG, SHORT or EXIT)
                        signal = SignalEvent(bars[0][0], bars[0][1], 'SHORT', 1)
                        self.events.put(signal)
                        self.bought[s] = True

                    elif self.bought[s]:
                        if self.send_exit(bars):
                            signal = SignalEvent(bars[0][0], bars[0][1], 'EXIT', 1)
                            self.events.put(signal)
                            self.bought[s] = False
                            self.wait_bars = len(self.study.data[s])

