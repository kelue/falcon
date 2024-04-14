from typing import List, Dict
from logger import logger
import json
import aiofiles
import asyncio
from models import TradeRequest, OrderType, ProductType
from utils import get_symbol_info, fetch_price

async def load_trade_data(filename="trades.json"):
    """Asynchronously loads trade data from the specified JSON file."""
    try:
        async with aiofiles.open(filename, 'r') as f:
            contents = await f.read()
            return json.loads(contents)
    except FileNotFoundError:
        return {}  # If file doesn't exist, start with an empty dictionary

async def save_trade_data(trade_data, filename="trades.json"):
    """Asynchronously saves the trade data dictionary to the specified JSON file."""
    async with aiofiles.open(filename, 'w') as f:
        await f.write(json.dumps(trade_data, indent=4)) 


def add_successful_trade(open_trades : Dict, symbol: str, trade_data: List[Dict]):
    open_trades[symbol] = open_trades.get(symbol, []) + trade_data
    asyncio.run(save_trade_data(open_trades))


async def monitor_stop_losses():
    from main import get_trading_service
    trading_service = get_trading_service()
    try:
        while True:
            open_trades = await load_trade_data()

            if not open_trades:
                break

            for symbol, trades in open_trades.items():
                current_price = fetch_latest_price(symbol)

                if not current_price: #skip this iteration id getting the price of the symbol fails
                    continue 

                for i in range(len(trades) - 1, -1, -1):  # Iterate backwards for removal
                    trade = trades[i]
                    if should_trigger_stoploss(trade, current_price):
                        trade_signal = build_rms_trade_request(trade, current_price)
                        res = trading_service.place_rms_order(trade_signal)
                        if res['status']:
                            remove_trade(open_trades, symbol, trade['pseudo_account'])

                asyncio.sleep(1) # Sleep for 1 second before checking next symbol
    except Exception as e:
        logger.exception("An error occurred during stop-loss monitoring:", exc_info=e)

def remove_trade(open_trades, symbol, pseudo_account):
    if symbol in open_trades:
        open_trades[symbol] = [
            trade for trade in open_trades[symbol] if trade['pseudo_account'] != pseudo_account
        ]
        if not open_trades[symbol]:  # Remove the symbol if no trades left
            del open_trades[symbol]
        asyncio.run(save_trade_data(open_trades))    


def should_trigger_stoploss(trade, current_price):
    stop_loss = trade['stoploss_price']
    trade_type = trade['trade_type']
    if not stop_loss:
       return False
    return current_price <= stop_loss if trade_type == 'BUY' else current_price >= stop_loss


def build_rms_trade_request(trade, current_price: float):
    #Logic to create a trade signal to counter the original trade
    counter_trade_type = 'SELL' if trade['trade_type'] == 'BUY' else 'BUY'

    trade_request = TradeRequest(
        pseudoAccount=trade['pseudo_account'],
        symbol=trade['symbol'],
        tradeType=counter_trade_type,
        orderType=OrderType.market,
        productType=ProductType.INTRADAY,
        quantity=trade['quantity'],
        price=current_price,
        triggerPrice=0 
    )
    return trade_request

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
        tokens_data[symbol] = token
        write_json_file(tokens_data)

        price = fetch_price(token)
        if price:
            return price
    return None
 
def get_symbol_token_data():
    try:
        return read_json_file()
    except FileNotFoundError:
        return {}
    
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
    return tokens_data.get(symbol, False)
   