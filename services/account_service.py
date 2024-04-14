import requests
import os
from models import Account
from logger import logger
class AccountService:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url

    def get_active_accounts(self) -> list[Account]:
        try:
            url = self.api_base_url

            response = requests.get(url)

            if response.status_code == 200:
                accounts_data = response.json().get('accountslist')
                return accounts_data
            else:
                return []

            #for testing
            # return [Account(pseudoAccountName="NPG0001", fund=100000, accountId="VL580K", stoplosstype="number", stoploss=1000)]
        except Exception as e:
            logger.exception("An error occurred during get_active_accounts:", exc_info=e)
        
    def get_user_demat(self, id) -> float:

        api_key = os.getenv("STOCKS_DEVELOPER_API_KEY")  
        url = "https://api.stocksdeveloper.in/trading/readPlatformMargins"
        headers = {'api-key': api_key}

        data = {'pseudoAccount': id}

        res = requests.get(url, headers=headers, data=data)

        if res.status == True and res.result != None:

            demat_margin = 0

            for margin in res.result:
                if margin.category == "EQUITY":
                    demat_margin += margin.funds
                    break 
                else:
                    continue

        return demat_margin            



        