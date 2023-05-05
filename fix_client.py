## Python version: 3.9.13

import quickfix as fix
import quickfix42 as fix42
import random
import time

class FixClient(fix.Application):

    def onCreate(self, session_id):
        self.session_id = session_id
        self.order_dict = {}
        self.pnl = 0.0
        self.total_volume = 0
        self.vwap_dict = {}
        
    def onLogon(self, session_id):
        print(f"Logon: {session_id}")

    def onLogout(self, session_id):
        print(f"Logout: {session_id}")

    def toAdmin(self, message, session_id):
        print(f"ToAdmin: {message}")

    def fromAdmin(self, message, session_id):
        print(f"FromAdmin: {message}")

    def toApp(self, message, session_id):
        print(f"ToApp: {message}")

    # Parse and handle incoming messages
    def fromApp(self, message, session_id):
        print(f"fromApp: {message}")
        msg_type = fix.MsgType()
        message.getHeader().getField(msg_type)
        #print(msg_type.getValue())
        if msg_type.getValue() == fix.MsgType_Reject: #3
            self.onOrderReject(message)
        elif msg_type.getValue() == fix.MsgType_ExecutionReport: #8
            self.onExecutionReport(message)
        elif msg_type.getValue() == fix.MsgType_OrderCancelReject: #9
            self.onCancelReject(message)

    def onOrderReject(self, reject):
        print(f"Reject: {reject}")

    def onExecutionReport(self, exec_report):
        print(f"Execution Report: {exec_report}")
        
        last_px = (float) (exec_report.getField(31)) 
        last_qty = (int) (exec_report.getField(32))
        exec_type = exec_report.getField(39) #exec_type
        side = exec_report.getField(54) #side
        symbol = exec_report.getField(55) #symbol

        if exec_type == fix.ExecType_FILL or exec_type == fix.ExecType_PARTIAL_FILL:
            self.total_volume += last_qty
            self.pnl += last_qty * last_px * (1 if side == fix.Side_BUY else -1)

            if symbol not in self.vwap_dict:
                self.vwap_dict[symbol] = {'total_volume': 0, 'total_value': 0}
            self.vwap_dict[symbol]['total_volume'] += last_qty
            self.vwap_dict[symbol]['total_value'] += last_qty * last_px

            print(f'Execution Report: Filled {last_qty} shares of {symbol} at ${last_px}')

    def onCancelReject(self, cancel_reject):
        print(f"Order Cancel Reject: {cancel_reject}")
    
    def createOrder(self,symbol, side, order_type, price, quantity, clOrdID):
        order = fix.Message()
        order.getHeader().setField(fix.BeginString(fix.BeginString_FIX42))
        order.getHeader().setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        order.setField(fix.ClOrdID(clOrdID))
        order.setField(fix.HandlInst(fix.HandlInst_MANUAL_ORDER_BEST_EXECUTION))
        order.setField(fix.Symbol(symbol))
        order.setField(fix.Side(side))
        order.setField(fix.OrdType(order_type))
        order.setField(fix.OrderQty(quantity))
        order.setField(fix.TransactTime())
        if order_type == fix.OrdType_LIMIT:
            order.setField(fix.Price(price))
        return order
    
    def cancelOrder(self,symbol, side, quantity, clOrdID, origClOrdID):
        order = fix.Message()
        order.getHeader().setField(fix.BeginString(fix.BeginString_FIX42))
        order.getHeader().setField(fix.MsgType(fix.MsgType_OrderCancelRequest))
        order.setField(fix.ClOrdID(clOrdID))
        order.setField(fix.OrigClOrdID(origClOrdID))
        order.setField(fix.Symbol(symbol))
        order.setField(fix.Side(side))
        order.setField(fix.OrderQty(quantity))
        order.setField(fix.TransactTime())
        return order

    def sendOrder(self, order):
        fix.Session.sendToTarget(order, self.session_id)


if __name__ == "__main__":
    try:
        settings = fix.SessionSettings("fix_client.cfg")
        application = FixClient()
        storeFactory = fix.FileStoreFactory(settings)
        logFactory = fix.FileLogFactory(settings)
        initiator = fix.SocketInitiator(application, storeFactory, settings, logFactory)
        initiator.start()

        time.sleep(5)  # Wait for logon before sending orders

        symbols = ["MSFT", "AAPL", "BAC"] #55
        sides = [fix.Side_BUY, fix.Side_SELL, fix.Side_SELL_SHORT] #54
        order_types = [fix.OrdType_LIMIT, fix.OrdType_MARKET] #40

        # send 1000 random orders
        for i in range(1000):
            symbol = random.choice(symbols)
            order_type = random.choice(order_types)
            side = random.choice(sides)
            price = round(random.uniform(1, 100), 2)
            qty = random.randint(1, 100)

            cl_ord_id = f"ORDER{i+1}"
            # Create and send a new order
            new_order = application.createOrder(symbol, side, order_type, price, qty, cl_ord_id)
            application.sendOrder(new_order)

            # Randomly send a cancel request
            if random.random() < 0.5:
                time.sleep(random.uniform(0.1, 0.3))
                cancel_request = application.cancelOrder(symbol, side, qty, f"CANCEL{i+1}", cl_ord_id)
                application.sendOrder(cancel_request)

            time.sleep(random.uniform(0.1, 0.3))

        time.sleep(5)

        initiator.stop()
        print("Total trading volume (USD):", application.total_volume)
        print("PNL (USD):", application.pnl)

        for symbol, data in application.vwap_dict.items():
            vwap = data['total_value'] / data['total_volume']
            print(f"VWAP for {symbol}: ${vwap:.2f}")

    except fix.ConfigError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Exception: {e}")
        
