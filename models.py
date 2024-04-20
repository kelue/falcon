from enum import Enum
from typing import List
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


#sub classes for tradesignal
#I am not sure these are the only strategy values for the strategyname field will have str for now
# TODO: verify the strategyname values
class StrategyName(str, Enum):
    chaipitepite = "chaipitepite"
    daily_khelo = "daily khelo"

class TradeType(str, Enum):
    option = "option"
    equity = "equity"

class SignalType(str, Enum):
    buy = "buy"
    sell = "sell"

    def upper(self):
        return self.value.upper()

class TradeSignal(BaseModel):
    symbolname: str
    signal: SignalType
    price: float  
    type: TradeType
    strategyname: str
    
#sub classes for trade request
class OrderType(str, Enum):
    market = "market"

class ProductType(str, Enum):
    INTRADAY = "INTRADAY"


class TradeSignalType(str, Enum):
    buy = "BUY"
    sell = "SELL"

class TradeRequest(BaseModel):
    pseudoAccount: str 
    symbol: str  
    tradeType: TradeSignalType
    orderType: OrderType
    productType: ProductType
    quantity: int 
    price: float  # Assuming you'll populate this dynamically
    triggerPrice: float  # Assuming you'll populate this dynamically

#classes for accounts
class Account(BaseModel):
    pseudoAccountName: str
    fund: float
    accountId: str
    stoplosstype: str
    stoploss: float

class Settings(BaseSettings):
    users_url: str
    smart_api_user: str
    smart_api_pass:str
    smart_api_key: str
    totp_key:str
    stock_developers_api_key:str

    model_config = SettingsConfigDict(env_file=".env")