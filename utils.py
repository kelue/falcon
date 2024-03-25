import os
import pyotp
from dotenv import load_dotenv
from SmartApi import smartConnect


user_data = {'status': False}

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
    rtoken = user_data['refreshToken']
    smartApi.generateToken(rtoken)


def get_symbol_info(symbol):
    if not user_data['status']:
        login_user()

    searchScripData = smartApi.searchScrip("NSE", symbol)

    if searchScripData['status']:
        symbols = searchScripData['data']

        for symbol in symbols:
            if symbol['tradingsymbol'] == symbol:
                return symbol['symboltoken']
            
