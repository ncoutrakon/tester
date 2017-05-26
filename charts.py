import pandas as pd
import datetime as dt
pd.set_option('display.width', 200)

tick_filename = "/users/ncoutrakon/.wine/drive_c/SierraChart/Data/CL_tick.txt"

# returns dictionary with key, value
# price, volume traded at price
def get_vol_profile(tick_df):

    vol_profile = {}
    for i in range(tick_df.shape[0]):
        bid_px, bid_vol = tick_df.ix[i, [4, 8]]
        ask_px, ask_vol = tick_df.ix[i, [3, 9]]

        # tallys volume traded on bid
        if bid_px not in vol_profile:
            vol_profile[bid_px] = bid_vol
        else:
            vol_profile[bid_px] += bid_vol

        # tallys volume traded on ask
        if ask_px not in vol_profile:
            vol_profile[ask_px] = ask_vol
        else:
            vol_profile[ask_px] += ask_vol

    return vol_profile


# Volume Bars
# returns pandas DataFrame
def get_vol_bars(tick_df, volume):
    vol_bars = []
    vol_counter = 0
    for i in range(tick_df.shape[0]):
        time = tick_df.index[i]
        high, low, close, vol = tick_df.ix[i, [3, 4, 5, 6]]

        if vol_counter == 0:
            vol_bars.append([time, close, high, low, close, vol])
            vol_counter += vol
        elif vol_counter + vol <= volume:
            vol_bars[-1][4] = close

            # updates new high, low for each volume bar
            if vol_bars[-1][2] < high:
                vol_bars[-1][2] = high
            if vol_bars[-1][3] > low:
                vol_bars[-1][3] = low

            vol_counter += vol
            vol_bars[-1][5] = vol_counter

        # if vol_counter will be greater than volume parameter
        # adds volume up to volume parameter to current bar and
        # creates a new bar
        elif vol_counter + vol > volume:
            if vol_bars[-1][2] < high:
                vol_bars[-1][2] = high
            if vol_bars[-1][3] > low:
                vol_bars[-1][3] = low
            vol_bars[-1][4] = close
            vol_bars[-1][5] = volume
            vol_counter = vol_counter + vol - volume
            vol_bars.append([time, close, high, low, close, vol])

    vol_bars = pd.DataFrame(vol_bars)
    vol_bars.columns = ["Timestamp", "Open", "High", "Low", "Close", "Volume"]
    return vol_bars


# Range Bars
# returns list of tuples
# first element of each tuple is timestamp of when bar starts
# second element is a dictionary where key, value is
# price, and a tuple of [bid volume, ask volume] calculated within specified range
def get_range_bars(tick_df, range_length):
    range_bars = []
    range_slice = {}
    prices = {}
    for i in range(tick_df.shape[0]):
        if len(prices) == 0:
            time = tick_df.index[i]
        close, bidvol, askvol = tick_df.ix[i, [5, 8, 9]]
        prices[close] = "X"
        range_counter = abs(min(list(prices.keys())) - max(list(prices.keys())))
        if range_counter > range_length:
            range_bars.append([time, range_slice])
            range_slice = {}
            prices = {}

        if close not in range_slice:
            range_slice[close] = [bidvol, askvol]
        else:
            range_slice[close] = [range_slice[close][0] + bidvol, range_slice[close][1] + askvol]
    return range_bars


# Loadtick data
tick_df = pd.read_csv(tick_filename)
tick_df.columns = ['Date', 'Time', 'Open', 'High', 'Low', 'Close',
                    'Vol', 'Trades', 'BidVol', 'AskVol']

# Turn Floats into Integers where XXXX represents $XX.XX in price
tick_df[["Open", "High", "Low", "Close"]] = \
    tick_df[["Open", "High", "Low", "Close"]].multiply(100).astype(int)

# Datetime Manipulation
tick_df.ix[tick_df["Time"].apply(lambda x: "." not in x), "Time"] += ".0"
tick_df["DateTime"] = tick_df["Date"] + tick_df["Time"]
tick_df["DateTime"] = pd.to_datetime(tick_df["DateTime"], format="%Y/%m/%d %H:%M:%S.%f")
tick_df["Date"] = pd.to_datetime(tick_df["Date"], format="%Y/%m/%d")
tick_df = tick_df.set_index(pd.DatetimeIndex(tick_df['DateTime']))
tick_df = tick_df.drop(tick_df.columns[10], axis=1)


# test each chart function using only data from "2017-05-03"
trade_date = dt.datetime.strptime("2017-05-03", "%Y-%m-%d")
test_df = tick_df.loc[tick_df["Date"] == trade_date]

vol_bars = get_vol_bars(test_df, 1000)
vol_profile = get_vol_profile(test_df)
range_bars = get_range_bars(test_df, 6)

print(vol_bars.head())
print(vol_profile)
print(range_bars)
