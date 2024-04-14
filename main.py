import os
from logger import logger
from fastapi import FastAPI, HTTPException
from models import TradeSignal, TradeType, TradeRequest, OrderType, ProductType, Account, TradeSignal
from services import trading_service, account_service
from dotenv import load_dotenv
import asyncio
import aiohttp
from rms import add_successful_trade, load_trade_data, monitor_stop_losses
from utils import get_symbol_info

load_dotenv()
app = FastAPI()

global is_monitoring_running

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
            open_trades = await load_trade_data() # Load open trades from file
            
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
                        add_successful_trade(open_trades, signal.symbolname, successful_trades)

                        # Start the monitoring thread if not running
                        if not is_monitoring_running:
                            asyncio.create_task(monitor_stop_losses()) 
                            is_monitoring_running = True
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
                        add_successful_trade(open_trades, signal.symbolname, successful_trades)

                        # Start the monitoring thread if not running
                        if not is_monitoring_running:
                            asyncio.create_task(monitor_stop_losses()) 
                            is_monitoring_running = True
                return {
                    'status': True,
                    'data': successful_trades
                }
        else:
            return {
                'status': False,
                'data': 'No active accounts found'
            }
    except FileNotFoundError as e:
        # Handle file not found error
        raise HTTPException(status_code=404, detail="Trade data file not found")

    except ValueError as e:
        # Handle invalid data format error
        raise HTTPException(status_code=400, detail="Invalid trade data format")

    except Exception as e:  # Catch-all for unexpected errors
        # Log the error with details (see below)
        logger.exception("An error occured during trade processing:", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.get("/health")
async def health_check():
    try:
        check1 = False
        check2 = False
        account_service = get_account_service()
        accounts: list[Account] = account_service.get_active_accounts()
        if accounts:
            check1 = True
        check2 = await get_symbol_info("SBIN-EQ")

        if check1 and check2:
            return {
                'status': True,
                'message': 'Service is healthy'
        }
    except Exception as e:
        logger.exception("An error occured during health check:", exc_info=e)
        return {
            'status': False,
            'message': 'Service is unhealthy'
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
        triggerPrice=0
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


def calculate_stop_loss_price(trade_data, stoploss_type: str, stoploss_value: float, balance: float):
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

    price = trade_data['price']
    quantity = trade_data['quantity']
    trade_type = trade_data['trade_type']

    if stoploss_type == 'number':
        stop_loss_price = price - (stoploss_value / quantity) if trade_type == 'BUY' else price + (stoploss_value / quantity)  
    elif stoploss_type == 'percentage':
        loss_per_share = (balance * (stoploss_value / 100)) / quantity
        stop_loss_price = price - loss_per_share if trade_type == 'BUY' else price + loss_per_share
    else:
        return None  # Handle invalid stop loss type

    return stop_loss_price
    

