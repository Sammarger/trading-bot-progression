from AlgorithmImports import *
# region imports
# endregion

class AdaptableBlackTapir(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2022, 5, 5)
        self.set_end_date(2023, 5, 5)
        self.set_cash(100000)
        
        self.symbol = self.add_equity("SPY", Resolution.MINUTE).Symbol
        self.rollingWindow = RollingWindow[TradeBar](2)
        self.consolidate(self.symbol, Resolution.DAILY, self.CustomBarHandler)
        
        #Liquidate assets 15 minutes before market close
        self.schedule.on( self.date_rules.every_day(self.symbol),
                         self.time_rules.before_market_close(self.symbol, 15), self.ExitPositions)

    def on_data(self, data):
        if not self.rollingWindow.is_ready:
            return

        if not (self.time.hour == 9 and self.time.minute == 31 ): #Algorithm should trade right after market open and 
           return                                                 # and no other time

        if data[self.symbol].open >= 1.01 * self.rollingWindow[0].Close: #Checks if open price is 1% higher than the last closing price
            self.set_holdings(self.symbol, -1)
        elif data[self.symbol].open <= 0.99 * self.rollingWindow[0].Close:
            self.set_holdings(self.symbol, 1)
            
    def CustomBarHandler(self, bar):
        self.rollingWindow.Add(bar)

    def ExitPositions(self):
        self.Liquidate(self.symbol)