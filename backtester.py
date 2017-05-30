# Declare the components with respective parameters
import queue
import data, strategy, portfolio, execution
from queue import Empty

events = queue.Queue()
bars = data.HistoricCSVDataHandler(events, "/Users/ncoutrakon/Desktop/", ["CL"])
port = portfolio.NotSoNaivePortfolio(bars, events, "2017-05-03", initial_capital=100000.0)
strategy = strategy.BracketStrategy(bars, port, events, 4, 12)
broker = execution.SimulatedExecutionHandler(bars, events)

i = 0
while i < 10000:
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
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    port.update_fill(event)


print(port.trade_activity)
