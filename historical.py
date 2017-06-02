# creates historical data files
# value areas, daily Volume Profile VAL, POC, VAH, and Daily High and Low
import pandas as pd


def get_hist_value_areas(date_df):
    # vp = dict((k, 0) for k, v in zip(date_df.Close, date_df.Vol))

    vp = pd.pivot_table(date_df, values="Vol", index="Close", aggfunc=sum)
    vp = vp.to_dict("index")

    vp = dict((k, v["Vol"]) for k, v in vp.items())
    hi, lo = max(k for k,v in vp.items()), min(k for k,v in vp.items())
    poc = max(vp, key=(lambda key: vp[key]))

    total_volume = sum(v for k, v in vp.items())
    va_threshold = .7 * total_volume
    va_volume = vp[poc]
    val, vah = 0, 0

    i = 1
    while va_volume < va_threshold:
        print(i)
        val = poc - i
        vah = poc + i
        if val in vp: va_volume += vp[val]
        if vah in vp: va_volume += vp[vah]
        i += 1

    return [hi, lo, val, poc, vah]

filename = "~/.wine/drive_c/SierraChart/Data/CL.txt"
tick_df = pd.read_csv(filename)

tick_df.columns = ['DateTime', 'Time', 'Open', 'High', 'Low', 'Close',
                    'Vol', 'Trades', 'BidVol', 'AskVol']

# Turn Floats into Integers where XXXX represents $XX.XX in price
tick_df[["Open", "High", "Low", "Close"]] = \
    tick_df[["Open", "High", "Low", "Close"]].multiply(100).astype(int)

# Datetime Manipulation
tick_df.ix[tick_df["Time"].apply(lambda x: "." not in x), "Time"] += ".0"
tick_df["DateTime"] = tick_df["DateTime"] + tick_df["Time"]
tick_df.index = pd.to_datetime(tick_df["DateTime"], format="%Y/%m/%d %H:%M:%S.%f")
tick_df.drop(["DateTime", "Time", "Trades", "BidVol", "AskVol"], axis = 1, inplace = True)

# split index by day for analysis
# needs to be changed further for session times, not strictly day
date_list = tick_df.groupby(tick_df.index.day)
date_list = [date[1] for date in date_list]
date_vp = list(map(lambda x: get_hist_value_areas(x), date_list))
dates = list(map(lambda x: x.index.date[1], date_list))

date_dict = dict((d, v) for d, v in zip(dates, date_vp))


