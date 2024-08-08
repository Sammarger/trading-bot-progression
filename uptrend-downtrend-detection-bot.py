# region imports
from AlgorithmImports import *
# endregion

from collections import deque

class DeterminedAsparagusManatee(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2024,1,1)
        self.set_cash(100000)
        self.spy = self.add_equity("SPY", Resolution.DAILY).symbol

        # self.sma = self.SMA(self.spy, 30, Resolution.DAILY) # Indicator resolution can't be smaller 
                                                              # than the resolution for the security itself

        # closing_prices = self.History(self.spy, 30, Resolution.DAILY)["close"] # History Request
        # for time, price in closing_prices.loc[self.spy].items():
        #     self.sma.Update(time, price) # Update the sma with the history request data

        # Implementing a custom simple moving average 
        self.sma = CustomSimpleMovingAverage("SMA", 30)
        self.register_indicator(self.spy, self.sma, Resolution.DAILY)

    def on_data(self, data: Slice):
        if not self.sma.is_ready: # Must check whether the indicator has 30 days of data recorded
            return

        # Saving the high and low
        hist = self.History(self.spy, timedelta(365), Resolution.DAILY) # Period of 365 days, not bars
        low = min(hist["low"])                                          # as bars would exclude non-trading days
        high = max(hist["high"])                                        # counting 1.5 years
        # Use min and max indicators 

        price = self.Securities[self.spy].Price

        # Check if price is within the 365 day high
        if price * 1.05 >= high and self.sma.Current.Value < price: 
            if not self.Portfolio["SPY"].IsLong: # Checks whether the portfolio already has a long position
                self.SetHoldings(self.spy, 0.9)
        # Check if price is within the 365 day low
        elif price * 0.95 <= low and self.sma.Current.Value > price:
            if not self.Portfolio["SPY"].IsShort:
                self.SetHoldings(self.spy, -0.9)

        else:
            self.Liquidate() # If there are no open positions, liquidate does nothing
        
        # Plotting the values 

        self.Plot("Benchmark", "52w-High", high)
        self.Plot("Benchmark", "52w-Low", low)
        self.Plot("Benchmark", "SMA", self.sma.Current.Value)
    
class CustomSimpleMovingAverage(PythonIndicator):

    def __init__(self, name, period):
        self.Name = name
        self.Time = datetime.min
        self.Value = 0
        self.queue = deque(maxlen = period)

    def Update(self, input):
        self.queue.appendleft(input.Close)
        self.Time = input.EndTime
        count = len(self.queue)
        self.Value = sum(self.queue) / count
        return(count == self.queue.maxlen)