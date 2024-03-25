import os
import pyotp
from dotenv import load_dotenv
from SmartApi import smartConnect


user_data = {}

load_dotenv()
totp_secret = os.getenv("TOTP_SECRET")
smartapiuser = os.getenv("SMARTAPI_USER")
smartapipass = os.getenv("SMARTAPI_PASS")
smartapikey = os.getenv("SMARTAPI_KEY")


smartApi = smartConnect(smartapikey)


def login_user():
    totp = pyotp.TOTP(totp_secret).now()

    user = smartApi.generateSession(smartapiuser, smartapipass, totp)

    if user['status']:
        user_data['status'] = True
        user_data['refreshToken'] = user['data']['refreshToken']


def refresh_auth():
    try:
        rtoken = user_data['refreshToken']
        user = smartApi.generateToken(rtoken)

        if user['data']['jwtToken']:
            return
    except KeyError:
        if user["errorcode"] in ["AB8050", "AB8051", "AB1011"]:
            login_user()
        


def get_symbol_info(symbol):
    if not user_data['status']:
        login_user()

    searchScripData = smartApi.searchScrip("NSE", symbol)

    if searchScripData['status']:
        symbols = searchScripData['data']

        for sym in symbols:
            if sym['tradingsymbol'] == symbol:
                return sym['symboltoken']
            
    if searchScripData['errorcode'] in ["AG8001", "AG8002", "AG8003"]:
        refresh_auth()
        get_symbol_info(symbol)

            
def fetch_price(token):
    mode="LTP"
    exchangeTokens= {
    "NSE": [
    token
    ]
    }
    marketData=smartApi.getMarketData(mode, exchangeTokens)

    if marketData['status']:
        return marketData['data']['fetched'][0]['ltp']
    
    elif marketData['errorcode'] in ["AG8001", "AG8002", "AG8003"]:
        refresh_auth()
        fetch_price(token)

    else:
        login_user()
        fetch_price(token)