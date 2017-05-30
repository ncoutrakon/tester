import pandas as pd
import datetime as dt

filename = "~/.wine/drive_c/SierraChart/Data/CL.txt"
tick_df = pd.read_csv(filename)

tick_df.columns = ['DateTime', 'Time', 'Open', 'High', 'Low', 'Close',
                    'Vol', 'Trades', 'BidVol', 'AskVol']

# Turn Floats into Integers wheare XXXX represents $XX.XX in price
tick_df[["Open", "High", "Low", "Close"]] = \
    tick_df[["Open", "High", "Low", "Close"]].multiply(100).astype(int)

# Datetime Manipulation
tick_df.ix[tick_df["Time"].apply(lambda x: "." not in x), "Time"] += ".0"
tick_df["DateTime"] = tick_df["DateTime"] + tick_df["Time"]
tick_df["DateTime"] = pd.to_datetime(tick_df["DateTime"], format="%Y/%m/%d %H:%M:%S.%f")
tick_df.drop(["Time", "Trades", "BidVol", "AskVol"], axis = 1, inplace = True)


# test each chart function using only data from "2017-05-03"
trade_date = dt.datetime.strptime("2017-05-20", "%Y-%m-%d")
test_df = tick_df.loc[tick_df["DateTime"] > trade_date]

test_df.to_csv("~/Desktop/CL.csv", index = False)