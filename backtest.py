import pandas as pd
import datetime as dt
import numpy as np
from decimal import Decimal

pd.set_option('display.width', 200)


data_bar = pd.read_csv("/users/ncoutrakon/.wine/drive_c/SierraChart/Data/CL_tick.txt")
data_bar.columns = ['Date', 'Time', 'Open', 'High', 'Low', 'Last', 'Vol','Trades', 'BidVol', 'AskVol']


data_bar[["Open", "High", "Low", "Last"]] = data_bar[["Open", "High", "Low", "Last"]].multiply(100).astype(int)

data_bar.ix[data_bar["Time"].apply(lambda x: "." not in x), "Time"] += ".0"

data_bar["DateTime"] = data_bar["Date"] + data_bar["Time"]
data_bar["DateTime"] = pd.to_datetime(data_bar["DateTime"], format="%Y/%m/%d %H:%M:%S.%f")
data_bar["Date"] = pd.to_datetime(data_bar["Date"], format="%Y/%m/%d")

print(data_bar.head(10))

vol_date = dt.datetime.strptime("2017-05-03", "%Y-%m-%d")
vol_df = data_bar.loc[data_bar.Date == vol_date]

vol_profile = {}
for i in range(vol_df.shape[0]):
    bid_px = vol_df.ix[i, 4]
    bid_vol = vol_df.ix[i, 8]
    ask_px = vol_df.ix[i, 3]
    ask_vol = vol_df.ix[i, 9]
    if not bid_px in vol_profile:
        vol_profile[bid_px] = bid_vol
    else:
        vol_profile[bid_px] += bid_vol

    if not ask_px in vol_profile:
        vol_profile[ask_px] = ask_vol
    else:
        vol_profile[ask_px] += ask_vol

print(vol_profile)



# Range Bars
# range_bars = []
# range_counter = 0
# for i in range(1000):
#      tick_high = data_bar.ix[i, 3]
#      tick_low = data_bar.ix[i, 4]
#      tick_range = tick_high - tick_low
#      tick_time = data_bar.ix[i, 1]
#
#     if range_counter == 0 :
#           range_bars.append([tick_time, tick_high, tick_low])
#           range_counter = tick_range
#     elif range_counter
#


# Volume Bars
# vol_bars = []
# vol_counter = 0
# for i in range(2000):
#     tick_high = data_bar.ix[i, 3]
#     tick_low = data_bar.ix[i, 4]
#     tick_vol = data_bar.ix[i, 6]
#     tick_time = data_bar.ix[i, 1]
#
#     if vol_counter == 0:
#         vol_bars.append([tick_time, tick_high, tick_low, tick_vol])
#         vol_counter += tick_vol
#     elif vol_counter + tick_vol <= 1000:
#         if vol_bars[-1][1] < tick_high:
#             vol_bars[-1][1] = tick_high
#         if vol_bars[-1][2] > tick_low:
#             vol_bars[-1][2] = tick_low
#         vol_counter += tick_vol
#         vol_bars[-1][3] = vol_counter
#     elif vol_counter + tick_vol > 1000:
#         vol_bars.append([tick_time, tick_high, tick_low, tick_vol])
#         if vol_bars[-1][1] < tick_high:
#             vol_bars[-1][1] = tick_high
#         if vol_bars[-1][2] > tick_low:
#             vol_bars[-1][2] = tick_low
#         vol_bars[-1][3] = 1000
#         vol_counter = vol_counter + tick_vol - 1000
#
#
# vol_bars = pd.DataFrame(vol_bars)
# print(vol_bars.head(20))