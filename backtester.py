# Declare the components with respective parameters
import queue
import data, study, strategy, portfolio, execution, performance
from queue import Empty
import pandas as pd
import numpy as np

pd.set_option('display.width', 200)
np.set_printoptions(suppress=True)

events = queue.Queue()
bars = data.HistoricCSVDataHandler(events, "/Users/ncoutrakon/Desktop/", ["CL"])
port = portfolio.NotSoNaivePortfolio(bars, events, "2017-05-03", initial_capital=100000.0)
study_vb = study.VolumeBars(bars, 1000)
study_vp = study.VolumeProfile(bars)
study_range = study.RangeBars(bars, 8)
strategy = strategy.RangeBar(bars, port, events, 4, 12, study_range)
broker = execution.SimulatedExecutionHandler(bars, events)


i = 0
while i < 500000:
    i += 1
    # Update the bars (specific backtest code, as opposed to live trading)
    if bars.continue_backtest:
        bars.update_bars()
    else:
        break

    # Handle the events
    while True:
        try:
            event = events.get(False)
        except Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    study_vb.update()
                    study_vp.update()
                    study_range.update()
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)
                    port.market_snapshot.append([bars.get_latest_bars(event.symbol)[0][1],
                                                 study_vp.data[event.symbol],
                                                 study_vb.data[event.symbol][-15:],
                                                 study_range.data[event.symbol][-3:]])

                elif event.type == 'FILL':
                    port.update_fill(event)

print(performance.clean_trade_activity(port.trade_activity["CL"]))