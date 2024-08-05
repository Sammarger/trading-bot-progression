# region imports
from AlgorithmImports import *
# endregion

class SwimmingGreenTapir(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2023, 2, 3)
        self.set_end_date(2024, 2, 3)
        self.set_cash(100000)

        spy = self.add_equity("SPY", Resolution.DAILY)
        # self.add_future, self.add_forex ...

        spy.set_data_normalization_mode(DataNormalizationMode.RAW)

        self.spy = spy.Symbol

        self.set_benchmark("SPY")
        self.set_brokerage_model(BrokerageName.InteractiveBrokersBrokerage, AccountType.MARGIN)

        self.entryPrice = 0
        self.period = timedelta(31)
        self.nextEntryTime = self.Time

    def on_data(self, data: Slice):
        price = data.Bars[self.spy].Close

        if not self.portfolio.invested:
             if self.nextEntryTime <= self.Time:
                self.market_order(self.spy, int(self.portfolio.cash / price))
                # Current cash is divided by the current price of spy

                self.Log("BUY SPY @" + str(price)) # Logs the price and ticker
                self.entryPrice = price

        elif self.entryPrice * 1.1 < price or self.entryPrice * 0.9 > price:
            self.liquidate(self.spy) # Liquidates all positions in portfolio
            self.Log("SELL SPY @" + str(price))
            self.nextEntryTime = self.Time + self.period
