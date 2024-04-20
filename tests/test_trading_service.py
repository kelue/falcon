import math
from models import Account, TradeSignal
from services import trading_service
import unittest
from unittest import TestCase

class TestTradingService(TestCase):
    def setUp(self):
        self.trading_service = trading_service.TradingService()

    def test_lot_size_banknifty(self):
        account = Account(fund=50000)
        signal = TradeSignal(symbolname='banknifty')
        expected_lot_size = math.ceil(account.fund / 25000 * 15)
        self.assertEqual(self.trading_service.self.trading_service.get_predefined_option_lot_size(account, signal), expected_lot_size)

    def test_lot_size_nifty(self):
        account = Account(fund=50000)
        signal = TradeSignal(symbolname='nifty')
        expected_lot_size = math.ceil(account.fund / 33000 * 50)
        self.assertEqual(self.trading_service.get_predefined_option_lot_size(account, signal), expected_lot_size)

    def test_lot_size_finnifty(self):
        account = Account(fund=50000)
        signal = TradeSignal(symbolname='finnifty')
        expected_lot_size = math.ceil(account.fund / 33000 * 40)
        self.assertEqual(self.trading_service.get_predefined_option_lot_size(account, signal), expected_lot_size)

    def test_lot_size_unknown_symbol(self):
        account = Account(fund=50000)
        signal = TradeSignal(symbolname='unknown')
        expected_lot_size = math.ceil(account.fund / 25000)
        self.assertEqual(self.trading_service.get_predefined_option_lot_size(account, signal), expected_lot_size)

    def test_lot_size_insufficient_balance(self):
        account = Account(fund=10000)
        signal = TradeSignal(symbolname='unknown')
        expected_lot_size = 0
        self.assertEqual(self.trading_service.get_predefined_option_lot_size(account, signal), expected_lot_size)

if __name__ == '__main__':
    unittest.main()