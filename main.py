import os
from fastapi import FastAPI
from models import TradeSignal, TradeType, TradeRequest, OrderType, ProductType, Account, TradeSignal
from services import trading_service, account_service
from dotenv import load_dotenv
import asyncio
import aiohttp


load_dotenv()
app = FastAPI()

def get_trading_service(): 
    return trading_service.TradingService() 

def get_account_service():
    url = os.getenv("USERS_URL")
    return account_service.AccountService(url)

@app.post("/open-trade")
async def process_trade_signal(signal: TradeSignal):

    trading_service = get_trading_service()
    account_service = get_account_service()

    accounts: list[Account] = account_service.get_active_accounts()

    successful_trades = [] 

    if accounts: 
        if signal.type == TradeType.equity:
            for account in accounts:
                lot_size = trading_service.calculate_lot_size(account, signal)
                trade_request = build_trade_request(account, signal, lot_size)
                order = trading_service.place_order(trade_request)
                if order['status']:
                    successful_trades.append({
                        'pseudo_account': account.pseudoAccountName,
                        'falcon_account': account.accountId 
                    })
            
            return {
                'status': True,
                'data': successful_trades
            }

        elif signal.type == TradeType.option:
            for account in accounts:
                lot_size = trading_service.get_predefined_option_lot_size(account.fund)
                trade_request = build_trade_request(account, signal, lot_size)
                order = trading_service.place_order(trade_request)
                if order['status']:
                    successful_trades.append({
                        'pseudo_account': account.pseudoAccountName,
                        'falcon_account': account.accountId 
                    })

            return {
                'status': True,
                'data': successful_trades
            }
    else:
        return {
            'status': False,
            'data': 'No active accounts found'
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