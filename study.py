

class Study(object):
    """
    Study is an abstract base class providing an interface for
    all subsequent (inherited) studies handling objects.

    The goal of a (derived) Study object is to restructure the inputs of Bars
    (OLHCVI) generated by a DataHandler object.

    This is designed to work both with historic and live data as
    the Study object is agnostic to the data source,
    since it obtains the bar tuples from a queue object.
    """
    pass

class VolumeBars(Study):
    def __init__(self, bars, volume):

        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.data = self.construct_all_studies()
        self.volume = volume

    def construct_all_studies(self):
        """
        Constructs the volume bars list using the start_date
        to determine when the time index will begin.
        """
        d = dict((k, v) for k, v in [(s, [[0, 0, 0, 0, 0, 0]]) for s in self.symbol_list])
        return d

    def calculate(self, bars, study):
        sym, time, open_px, high, low, close, vol = bars[0]
        vol_counter = study[-1][5]

        if vol_counter == 0:
            study.append([time, close, high, low, close, vol])

        elif vol_counter + vol <= self.volume:
            study[-1][4] = close

            # updates new high, low for each volume bar
            if study[-1][2] < high:
                study[-1][2] = high
            if study[-1][3] > low:
                study[-1][3] = low

            vol_counter += vol
            study[-1][5] = vol_counter

        # if vol_counter will be greater than volume parameter
        # adds volume up to volume parameter to current bar and
        # creates a new bar
        elif vol_counter + vol > self.volume:
            if study[-1][2] < high:
                study[-1][2] = high
            if study[-1][3] > low:
                study[-1][3] = low
            study[-1][4] = close
            study[-1][5] = self.volume
            vol = vol_counter + vol - self.volume
            study.append([time, close, high, low, close, vol])

        return study

    def update(self):
         for s in self.symbol_list:
            bars = self.bars.get_latest_bars(s, N=1)
            if bars is not None and bars != []:
                self.data[s] = self.calculate(bars, self.data[s])


class VolumeProfile(Study):
    def __init__(self, bars):

        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.data = self.construct_all_studies()

    def construct_all_studies(self):
        """
        Constructs the volume bars list using the start_date
        to determine when the time index will begin.
        """
        d = dict((k, v) for k, v in {s, {0: 0}} for s in self.symbol_list)
        return d

    def calculate(self, bars, study):
        sym, time, open_px, ask, bid, trade_px, vol = bars[0]

        # tallys volume traded on bid
        if trade not in study:
            study[trade_px] = vol
        else:
            study[trade_px] += vol

        return study

    def update(self):
         for s in self.symbol_list:
            bars = self.bars.get_latest_bars(s, N=1)
            if bars is not None and bars != []:
                self.data[s] = self.calculate(bars, self.data[s])