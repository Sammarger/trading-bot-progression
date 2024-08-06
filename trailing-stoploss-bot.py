# region imports
from AlgorithmImports import *
# endregion

# This bot introduces the function on_order_event, as well as using entryTicket and stopMarket to identifing the stop loss order

class CasualBlackJaguar(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2023, 2, 5)
        self.set_end_date(2024,2,5)
        self.set_cash(100000)
        self.qqq = self.add_equity("QQQ", Resolution.HOUR).symbol

        self.entryTicket = None
        self.stopMarketTicket = None
        
        #Used to make sure to wait 30 days before starting to invest again # Tracks Fill time
        self.entryTime = datetime.min 
        self.stopMarketOrderFillTime = datetime.min

        # Takes the highest price and calculates whther the current price is 5% below said price
        self.highestPrice = 0 



    def on_data(self, data: Slice):
        # Check whether 30 days has passed since closing the last position
        if (self.Time - self.stopMarketOrderFillTime).days < 30:
            return
        
        price = self.securities[self.qqq].Price

        # Send entry limit order for as many shares of QQQ
        if not self.portfolio.invested  and not self.transactions.get_open_orders(self.qqq): # Check if already invested or if there are already open orders for qqq
            quantity = self.calculate_order_quantity(self.qqq, 0.9)
            self.entryTicket = self.limit_order(self.qqq, quantity, price, "Entry Order")
            self.entryTime = self.Time

        # If limit order order is not filled in one day, increase limit price
        if (self.Time - self.entryTime).days > 1 and self.entryTicket.status != OrderStatus.FILLED:
            self.entryTime = self.Time
            updateFields = UpdateOrderFields()
            updateFields.limit_price = price
            self.entryTicket.update(updateFields)

        # Move up the price of the trailing stop loss if necessary
        if self.stopMarketTicket is not None and self.portfolio.invested:
            if price > self.highestPrice:
                self.highestPrice = price
                self.debug(self.highestPrice)
                updateFields = UpdateOrderFields()
                updateFields.stop_price = price * 0.95
                self.stopMarketTicket.update(updateFields)



    def on_order_event(self, order_event):
        if order_event.status !=  OrderStatus.FILLED:
            return

        # Send stop loss order if entry limit order is filled
        if self.entryTicket is not None and self.entryTicket.order_id == order_event.order_id:
            self.stopMarketTicket = self.stop_market_order(self.qqq, -self.entryTicket.quantity, 0.95*self.entryTicket.average_fill_price) # Quantity is negative as we are selling

        # Save Fill time of stop loss order
        if self.stopMarketTicket is not None and self.stopMarketTicket.order_id == order_event.order_id:
            self.stopMarketOrderFillTime = self.Time
            self.highestPrice = 0 

     