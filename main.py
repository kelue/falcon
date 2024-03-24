import os
from fastapi import FastAPI
from models import TradeSignal, TradeType, TradeRequest, OrderType, ProductType, Account, TradeSignal
from services import trading_service, account_service
from dotenv import load_dotenv
import asyncio
import aiohttp
from typing import Dict

load_dotenv()
app = FastAPI()

def get_trading_service(): 
    return trading_service.TradingService() 

def get_account_service():
    url = os.getenv("USERS_URL")
    return account_service.AccountService(url)

@app.post("/opentrade")
async def process_trade_signal(signal: TradeSignal):
    try:

        trading_service = get_trading_service()
        account_service = get_account_service()

        accounts: list[Account] = account_service.get_active_accounts()

        successful_trades = [] 

        if accounts: 
            tasks = []
            if signal.type == TradeType.equity:
                async with aiohttp.ClientSession() as session:  # Shared session for efficiency
                    for account in accounts:
                        demat_margin = account_service.get_user_demat(account.pseudoAccountName)

                        if demat_margin:
                            account.fund = demat_margin

                        lot_size = trading_service.calculate_lot_size(account, signal)
                        trade_request = build_trade_request(account, signal, lot_size)
                        tasks.append(asyncio.create_task(trading_service.place_order(trade_request, account)))

                        results = await asyncio.gather(*tasks)  
                        successful_trades = get_successful_trades(results)
                return {
                    'status': True,
                    'data': successful_trades
                }

            elif signal.type == TradeType.option:
                async with aiohttp.ClientSession() as session:  # Shared session for efficiency
                    for account in accounts:
                        demat_margin = account_service.get_user_demat(account.pseudoAccountName)

                        if demat_margin:
                            account.fund = demat_margin
                        if account.fund < 100000:
                            continue
                        lot_size = trading_service.get_predefined_option_lot_size(account, signal)
                        trade_request = build_trade_request(account, signal, lot_size)
                        tasks.append(asyncio.create_task(trading_service.place_order(trade_request)))

                        results = await asyncio.gather(*tasks)  
                        successful_trades = get_successful_trades(results)
                return {
                    'status': True,
                    'data': successful_trades
                }
        else:
            return {
                'status': False,
                'data': 'No active accounts found'
            }
    except Exception as e:
        return {
            "error": "INTERNAL SERVER ERROR",
            "message": "server error {}".format(e)
        }

# Helper functions
def build_trade_request(account: Account, signal: TradeSignal, lot_size: int):
    trade_request = TradeRequest(
        pseudoAccount=account.pseudoAccountName,
        symbol=signal.symbolname.lower(),
        tradeType=signal.signal.upper(), 
        orderType=OrderType.market,  
        productType=ProductType.INTRADAY,  
        quantity=lot_size,
        price=signal.price,  
        triggerPrice=0  # You might need conditional logic to set this
    )
    return trade_request

def get_successful_trades(results):
    successful_trades = []
    for result in results:
        if result['status']:  # Check if order was successful
            # Fetch stop-loss information from the account (you'll need to implement this)
            stoploss_type = result['data']['stoplosstype']
            stoploss_value = result['data']['stoploss']

            trade_data = {
                'pseudo_account': result['data']['account'],
                'falcon_account': result['data']['account_id'],
                'symbol': result['data']['symbol'],
                'order_id': result['data']['order_id'],
                'quantity': result['data']['quantity'],
                'price': result['data']['price'],
                'balance': result['data']['balance'],
                'trade_type': result['data']['trade_type'],
            }

            stoploss_price = calculate_stop_loss_price(trade_data, stoploss_type, stoploss_value)

            successful_trades.append({
                **trade_data,  # Unpack previous trade data
                'stoploss_price': stoploss_price
            })
    return successful_trades


def calculate_stop_loss_price(trade_data : Dict, stoploss_type: str, stoploss_value: float, balance: float):
    """
    Calculates the stop-loss price based on the user's stop loss preferences and trade type.

    Args:
        trade_data (dict): Successful trade data containing 'quantity', 'price', and 'trade_type'
        stoploss_type (str): 'number' or 'percentage'
        stoploss_value (float): The stop-loss value (either amount or percentage).
        balance (float): The user's account balance.
        trade_type (str): 'BUY' or 'SELL'

    Returns:
        float: The calculated stop-loss price.
    """

    if stoploss_type == 'number':
        if trade_data['trade_type'] == 'BUY':
            stop_loss_price = trade_data['price'] - (stoploss_value / trade_data['quantity'])
        elif trade_data['trade_type'] == 'SELL':
            stop_loss_price = trade_data['price'] + (stoploss_value / trade_data['quantity'])
    elif stoploss_type == 'percentage':
        max_loss_amount = balance * (stoploss_value / 100)
        loss_per_share = max_loss_amount / trade_data['quantity']
        if trade_data['trade_type'] == 'BUY':
            stop_loss_price = trade_data['price'] - loss_per_share
        elif trade_data['trade_type'] == 'SELL':
            stop_loss_price = trade_data['price'] + loss_per_share
    else:
        return None  # Handle invalid stop loss type

    return stop_loss_price

