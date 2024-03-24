import os
from dotenv import load_dotenv
from models import TradeRequest, Account, TradeSignal
import requests
import math
import aiohttp

load_dotenv()

class TradingService:
    def calculate_lot_size(self, account: Account, signal: TradeSignal):
        price = signal.price
        fund = account.fund

        lot_size = round(fund / price, 1)
        return lot_size
    
    

    def get_predefined_option_lot_size(self, account: Account, signal: TradeSignal) -> int:
        """
        Calculate the lot size for a predefined option based on the account balance and signal symbol.

        Args:
            account (Account): The trading account.
            signal (TradeSignal): The trade signal.

        Returns:
            int: The calculated lot size.

        Raises:
            None

        """
        lot_sizes = {
            'banknifty': (15, 25000),  # quantity, perLot 
            'finnifty': (40, 33000),
            'nifty': (50, 33000),
        }

        demat_balance = account.fund 

        for key in lot_sizes:
            if key.lower() in signal.symbolname.lower():
                quantity, per_lot = lot_sizes[key]
                calc = demat_balance / per_lot
                lot_size = math.ceil(calc * quantity) 
                return lot_size

        lot_size = math.ceil(demat_balance / 25000)
        return lot_size

    async def place_order(self, trade_request: TradeRequest, account: Account):
        api_key = os.getenv("STOCKS_DEVELOPER_API_KEY")  
        url = "https://api.stocksdeveloper.in/trading/placeRegularOrder"
        headers = {'api-key': api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=trade_request.model_dump(mode="json")) as response:
                    response.raise_for_status()  # Ensure successful status
                    api_response = await response.json()
                    if api_response.get('status'):
                        return {  # Return details on success
                            'status': True,
                            'data': {
                                'order_id': api_response.get('result'),
                                'account': account.pseudoAccountName,
                                'account_id': account.accountId,
                                'balance': account.fund,
                                'symbol': trade_request.symbol,
                                'trade_type': trade_request.tradeType,
                                'quantity': trade_request.quantity,
                                'price': trade_request.price,
                                'stoplosstype': account.stoplosstype,
                                'stoploss': account.stoploss
                            }
                        }
                    else:
                        return {
                            'status': False,
                            'message': api_response.get('message', 'API error')
                        }
                
        except aiohttp.ClientError as e:
            return {
                'status': False,
                'message': f'Cannot connect to API: {str(e)}'
            }             

        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Cannot connect to API: {str(e)}'
            }
