import os
from dotenv import load_dotenv
from models import TradeRequest, Account, TradeSignal
import requests
import math

load_dotenv()

class TradingService:
    def calculate_lot_size(self, account: Account, signal: TradeSignal):
        price = signal.price
        fund = account.fund

        lot_size = round(fund / price, 1)
        return lot_size
    
    

    def get_predefined_option_lot_size(account: Account, signal: TradeSignal) -> int:
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
            'nifty': (50, 33000),
            'finnifty': (40, 33000)
        }

        demat_balance = account.fund 

        for key in lot_sizes:
            if key.lower() in signal.symbolname.lower():
                quantity, per_lot = lot_sizes[key]
                calc = demat_balance / per_lot
                lot_size = math.ceil(calc * quantity) 
                return lot_size

        if demat_balance < 25000:
            return 0

        lot_size = math.ceil(demat_balance / 25000)
        return lot_size

    def place_order(self, trade_request: TradeRequest):
        api_key = os.getenv("STOCKS_DEVELOPER_API_KEY")  
        url = "https://api.stocksdeveloper.in/trading/placeRegularOrder"
        headers = {'api-key': api_key}

        try:
            response = requests.post(url, headers=headers, data=trade_request.model_dump(mode="json")) 

            if response.status_code == 200:
                api_response = response.json()
                if api_response.get('status'):
                    return {
                        'status': True,
                        'result': api_response.get('result')
                    }
                else:
                    return {
                        'status': False,
                        'message': api_response.get('message', 'API error')
                    }

            else:
                return {
                    'status': False,
                    'message': f'API request failed with status code: {response.status_code}'
                }

        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'message': f'Cannot connect to API: {str(e)}'
            } 
