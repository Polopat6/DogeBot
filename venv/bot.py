import websocket, json, talib, pprint, numpy, talib
import config
from binance.enums import *
from binance.client import Client

RSI_PERIOD = 14
OVERSOLD_THRESHOLD = 30
OVERBOUGHT_THRESHOLD = 70
TRADE_QUANTITY = 5.00
TRADE_SYMBOL = 'DOGE_USDT'
SOCKET = 'wss://stream.binance.com:9443/ws/dogeusdt@kline_1m'

closes = []
in_position = False
client = Client(config.API_KEY, config.API_SECRET, tld='us')


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print('sendinf order')
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        return False

    return True


def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes
    print(message)
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print('candle closed at {}'.format(close))
        closes.append(float(close))
        print('closes')
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print('all rsis claculated so far')
            print(rsi)
            last_rsi = rsi[-1]
            print('the current rsi is {}'.format(last_rsi))

            if last_rsi > OVERBOUGHT_THRESHOLD:
                if in_position:
                    print('Overbought, sell! sell! sell!')
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print('We dont own any')

            if last_rsi < OVERSOLD_THRESHOLD:
                if in_position:
                    print('It is oversold but you already own it, nothing to do')
                else:
                    print('Buy! Buy! Buy!')
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True



ws = websocket.WebSocketApp(SOCKET, on_open=on_open , on_close=on_close , on_message=on_message)
ws.run_forever()