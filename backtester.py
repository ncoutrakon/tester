# Declare the components with respective parameters
import queue
import data, study, strategy, portfolio, execution
from queue import Empty
import pandas as pd

pd.set_option('display.width', 200)


events = queue.Queue()
bars = data.HistoricCSVDataHandler(events, "/Users/ncoutrakon/Desktop/", ["CL"])
port = portfolio.NotSoNaivePortfolio(bars, events, "2017-05-03", initial_capital=100000.0)
study = study.VolumeBars(bars, 1000)
strategy = strategy.BracketStrategy(bars, port, events, 4, 12, study)
broker = execution.SimulatedExecutionHandler(bars, events)


i = 0
while i < 100000:
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
                    study.update()
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    port.update_fill(event)

print(pd.DataFrame(study.data["CL"]))
print(pd.DataFrame(port.trade_activity))
