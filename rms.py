
import os
from main import get_trading_service
import time
import json
from dotenv import load_dotenv
from utils import get_symbol_info, fetch_price

# load_dotenv()
# totp_secret = os.getenv("TOTP_SECRET")
# smartapiuser = os.getenv("SMARTAPI_USER")
# smartapipass = os.getenv("SMARTAPI_PASS")
# smartapikey = os.getenv("SMARTAPI_KEY")

open_trades = {}  # Dictionary to store open trades

#TODO: write function to expose functionality to add successfult trades to open-trades with symbol as key

def monitor_stop_losses():
    trading_service = get_trading_service()

    while True:
        for symbol, trades in open_trades.items():
            current_price = fetch_latest_price(symbol)

            if not current_price: #skip this iteration id getting the price of the symbol fails
                continue 

            for i in range(len(trades) - 1, -1, -1):  # Iterate backwards for removal
                trade = trades[i]
                if should_trigger_stoploss(trade, current_price):
                    trade_signal = build_rms_trade_request(trade) #TODO write function to generate trade request with info in trade dict
                    trading_service.place_order(trade_signal, trade['account']) #TODO place order without creating new successful trade to track
                    remove_trade(symbol, trade['pseudo_account'])

        time.sleep(5)  #TODO Adjust polling interval as needed

def add_trade(symbol, trade_data):
    if symbol not in open_trades:
        open_trades[symbol] = []
    open_trades[symbol].append(trade_data)


def remove_trade(symbol, pseudo_account):
    if symbol in open_trades:
        open_trades[symbol] = [
            trade for trade in open_trades[symbol] if trade['pseudo_account'] != pseudo_account
        ]
        if not open_trades[symbol]:  # Remove the symbol if no trades left
            del open_trades[symbol]   


def should_trigger_stoploss(trade, current_price):
    if trade['trade_type'] == 'BUY':
        return current_price <= trade['stoploss_price']
    elif trade['trade_type'] == 'SELL':
        return current_price >= trade['stoploss_price']
    else:
        return False  #TODO Handle invalid trade types


def build_rms_trade_request(trade):
    #TODO ... Logic to create a trade signal to counter the original trade
    counter_trade_type = 'SELL' if trade['trade_type'] == 'BUY' else 'BUY' 

    pass

def fetch_latest_price(symbol: str):
   
    token = get_token_from_file(symbol)

    if token:
        price = fetch_price(token)  #implement fetch price
        if price:
            return price
    else:
        #token does not exist so fetch token then get price
        token = get_symbol_info(symbol)
        #fetch price after getting token and append token to token-symbol file
        tokens_data = get_symbol_token_data()
        tokens_data.append({symbol:token})
        write_json_file(tokens_data)

        price = fetch_price(token)
        if price:
            return price
    return None
 
def get_symbol_token_data():
    try:
        return read_json_file()
    except FileNotFoundError:
        return []
    
def read_json_file():
    with open("symbol_tokens.json", 'r') as file:
        return json.load(file)
    
def write_json_file(data):
    with open("symbol_tokens.json", 'w') as file:
        return json.dump(data, file, indent=4)
 
def get_token_from_file(symbol):
    """
    Retrieves the token associated with the given symbol from the token data file.

    Args:
        symbol (str): The symbol to search for.

    Returns:
        str or bool: The token associated with the symbol if found, False otherwise.
    """
    tokens_data = get_symbol_token_data()
    for entry in tokens_data:
        if symbol in entry:  
            return entry[symbol] 
    return False
   