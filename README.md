# FIX Client Simulator

This is a simple FIX client implementation in Python for algorithmic trading using the QuickFIX library. The client connects to a FIX server and sends random orders for buying, selling, and short selling stocks. The client also supports order cancellation and metrics calculation included total trading volume, the profit and loss generated, and the Volume Weighted Average Price (VWAP) for each stock.

## Dependencies

- Python 3.9.13
- QuickFix 4.2

## Usage

1. Clone this repository / Copy all the files.
2. Install the dependencies: `pip install quickfix`. 
3. Update the `fix_client.cfg` file with the FIX server details.
4. Run the script: `python fix_client.py`.

## Features

- Connect to a FIX server using the SocketInitiator.
- Support sending new orders (35=D), including limit orders and market orders, for multiple stock symbols.
- Support order cancel request (35=F).
- Parse and handle incoming messages such as order rejects (35=3), execution reports (35=8), and cancel rejects (35=9).
- Calculate trading volume, PNL and the VWAP for each stock symbol.
- Log FIX messages for debugging and auditing purposes.

## FIX Client Configuration

The client configuration is stored in the `fix_client.cfg` file. Update this file with the appropriate settings for your FIX server before running the script.

```ini
[DEFAULT]
ConnectionType=initiator
ReconnectInterval=5
FileStorePath=store
FileLogPath=log
StartTime=00:00:00
EndTime=00:00:00
UseDataDictionary=N
DataDictionary=FIX42.xml
SocketConnectHost=FIX_SERVER_IP_ADDRESS
SocketConnectPort=FIX_SERVER_PORT
SenderCompID=SENDER_COMP_ID
TargetCompID=TARGET_COMP_ID
HeartBtInt=30
ResetOnLogon=Y

# Sequence number reset time
[SESSION]
BeginString=FIX.4.2
EndTime=23:59:59
StartTime=00:00:00
ResetOnLogout=Y
ResetOnDisconnect=Y
RefreshOnLogon=Y
ResetSeqNumFlag=Y

```

## Example Output

```
Logon: FIX.4.2:SENDER_COMP_ID->TARGET_COMP_ID
toApp: 8=FIX.4.2|9=180|35=D|...
...
fromApp: 8=FIX.4.2|9=180|35=8|...
Execution Report: Filled 50 shares of MSFT at $84.24
fromApp: 8=FIX.4.2|9=180|35=8|...
Execution Report: Filled 25 shares of AAPL at $99.79
...
Total trading volume (USD): 10000
PNL (USD): 950.23
VWAP for MSFT: $86.25
VWAP for AAPL: $102.35
VWAP for BAC: $50.75
```

## Functions

In the `FixClient` class, each function serves a specific purpose in handling the communication between the client (initiator) and the FIX server (acceptor). Here's a brief explanation of each function, add your custom code to handle specific messages.

| Function | Description |
|---|---|
| `onCreate(self, session_id)` | This function is called when a new session is created. It initialises the session_id, order_dict, pnl, total_volume, and vwap_dict variables. | 
| `onLogon(self, session_id)` | This function is called when the client successfully login to the FIX server. It prints the logon message with the session_id. |
| `onLogout(self, session_id)` | This function is called when the client logout from the FIX server. It prints the logout message with the session_id. |
| `toAdmin(self, message, session_id)` | This function is called when the client sends an administrative message to the server. It prints the outgoing administrative message. |
| `fromAdmin(self, message, session_id)` | This function is called when the client receives an administrative message from the server. It prints the incoming administrative message. |
| `toApp(self, message, session_id)` | This function is called when the client sends an application message to the server. It prints the outgoing application message. |
| `fromApp(self, message, session_id)` | This function is called when the client receives an application message from the server. It prints the incoming application message and handles different types of messages by calling the corresponding functions. |
| `onOrderReject(self, reject)` | This function is called when the client receives an order reject message. It prints the reject message. |
| `onExecutionReport(self, exec_report)` | This function is called when the client receives an execution report message. It processes the report by updating the pnl, total_volume, and vwap_dict variables and prints the execution report details. |
| `onCancelReject(self, cancel_reject)` | This function is called when the client receives an order cancel reject message. It prints the cancel reject message. |
| `createOrder(self, symbol, side, order_type, price, quantity, clOrdID)` | This function creates a new order message with the given parameters and returns the order message object. |
| `cancelOrder(self, symbol, side, quantity, clOrdID, origClOrdID)` | This function creates a new order cancel request message with the given parameters and returns the cancel request message object. |
| `sendOrder(self, order)` | This function sends the given order or cancel request message to the server using the session_id. |

The main part of the script (`if __name__ == "__main__":`) initialises the FixClient, connects to the FIX server, sends random orders, and calculates the VWAP and PNL for each stock symbol. It also handles exceptions and stops the initiator before exiting.
