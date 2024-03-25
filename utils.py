import os
import pyotp
from dotenv import load_dotenv
from SmartApi.smartConnect import SmartConnect

user_data = {}

load_dotenv()
totp_secret = os.getenv("TOTP_SECRET")
smartapiuser = os.getenv("SMARTAPI_USER")
smartapipass = os.getenv("SMARTAPI_PASS")
smartapikey = os.getenv("SMARTAPI_KEY")


smartApi = SmartConnect(smartapikey)


def login_user():
    totp = pyotp.TOTP(totp_secret).now()

    user = smartApi.generateSession(smartapiuser, smartapipass, totp)

    if user['status']:
        user_data['status'] = True
        user_data['refreshToken'] = user['data']['refreshToken']


def refresh_auth():
    if 'refreshToken' in user_data:  # Check for 'refreshToken' key
        rtoken = user_data['refreshToken']
        user = smartApi.generateToken(rtoken)

        if 'data' in user and 'jwtToken' in user['data']:  # Check for 'data' and 'jwtToken'
            return 
    if user.get("errorcode") in ["AB8050", "AB8051", "AB1011"]: 
        login_user()
        


def get_symbol_info(symbol):
    if not user_data['status']:
        login_user()

    searchScripData = smartApi.searchScrip("NSE", symbol)

    if searchScripData.get('status'):  # Safely check 'status'
        symbols = searchScripData.get('data', [])  # Default to an empty list
        for sym in symbols:
            if sym.get('tradingsymbol') == symbol: 
                return sym.get('symboltoken')      
    if searchScripData.get('errorcode') in ["AG8001", "AG8002", "AG8003"]:
        refresh_auth()
        get_symbol_info(symbol)
    if searchScripData.get("errorcode") in ["AB8050", "AB8051", "AB1011"]: 
        login_user()
        get_symbol_info(symbol)

            
def fetch_price(token):
    mode="LTP"
    exchangeTokens= {
    "NSE": [
             token
        ]
    }
    marketData=smartApi.getMarketData(mode, exchangeTokens)

    if 'status' in marketData:  # Check for 'status' key first
        if marketData['status']:
            if 'data' in marketData and 'fetched' in marketData['data'] and marketData['data']['fetched']:
                return marketData['data']['fetched'][0]['ltp']  
    elif 'errorcode' in marketData and marketData['errorcode'] in ["AG8001", "AG8002", "AG8003"]:
        refresh_auth()
        fetch_price(token)
    else:  
        login_user()
        fetch_price(token)