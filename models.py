from enum import Enum
from typing import List
from pydantic import BaseModel, validator

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

    # Pydantic validator similar to Laravel syntax
    @validator('symbolname') 
    def symbolname_must_be_valid(cls, value):
        allowed_symbols = ["finnifty", "nifty", "banknifty"]
        if not any(symbol in value.lower() for symbol in allowed_symbols):
            raise ValueError('Invalid symbolname')
        return value
    
#sub classes for trade request
class OrderType(str, Enum):
    market = "market"

class ProductType(str, Enum):
    INTRADAY = "INTRADAY"

class TradeRequest(BaseModel):
    pseudoAccount: str 
    symbol: str  
    tradeType: SignalType
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

class AccountListResponse(BaseModel):
    accountslist: List[Account]