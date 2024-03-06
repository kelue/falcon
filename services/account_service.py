import requests
from models import AccountListResponse, Account

class AccountService:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url

    def get_active_accounts(self) -> list[Account]:
        url = self.api_base_url

        response = requests.get(url)

        if response.status_code == 200:
            accounts_data = response.json()
            account_list_response = AccountListResponse(**accounts_data)
            return account_list_response.accountslist
        else:
            return []