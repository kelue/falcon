import asyncio
from unittest import TestCase, mock
from models import TradeSignal, Account, TradeType
from services import trading_service, account_service
from main import process_trade_signal

class TestProcessTradeSignal(TestCase):
    def setUp(self):
        self.mock_trading_service = mock.Mock(spec=trading_service.TradingService)
        self.mock_account_service = mock.Mock(spec=account_service.AccountService)

    def test_process_trade_signal_equity(self):
        signal = TradeSignal(type=TradeType.equity)
        account1 = Account(fund=50000)
        account2 = Account(fund=60000)
        self.mock_account_service.get_active_accounts.return_value = [account1, account2]
        self.mock_trading_service.calculate_lot_size.return_value = 10
        self.mock_trading_service.place_order.return_value = {'pseudo_account': '123', 'falcon_account': '456'}

        result = asyncio.run(process_trade_signal(signal, self.mock_trading_service, self.mock_account_service))

        self.assertTrue(result['status'])
        self.assertEqual(result['data'], [{'pseudo_account': '123', 'falcon_account': '456'}])
        self.mock_account_service.get_active_accounts.assert_called_once()
        self.mock_trading_service.calculate_lot_size.assert_called_with(account1, signal)
        self.mock_trading_service.place_order.assert_called_with(mock.ANY)

    def test_process_trade_signal_option(self):
        signal = TradeSignal(type=TradeType.option)
        account1 = Account(fund=150000)
        account2 = Account(fund=200000)
        self.mock_account_service.get_active_accounts.return_value = [account1, account2]
        self.mock_trading_service.get_predefined_option_lot_size.return_value = 20
        self.mock_trading_service.place_order.return_value = {'pseudo_account': '789', 'falcon_account': '012'}

        result = asyncio.run(process_trade_signal(signal, self.mock_trading_service, self.mock_account_service))

        self.assertTrue(result['status'])
        self.assertEqual(result['data'], [{'pseudo_account': '789', 'falcon_account': '012'}])
        self.mock_account_service.get_active_accounts.assert_called_once()
        self.mock_trading_service.get_predefined_option_lot_size.assert_called_with(account1, signal)
        self.mock_trading_service.place_order.assert_called_with(mock.ANY)

    def test_process_trade_signal_no_active_accounts(self):
        signal = TradeSignal(type=TradeType.equity)
        self.mock_account_service.get_active_accounts.return_value = []

        result = asyncio.run(process_trade_signal(signal, self.mock_trading_service, self.mock_account_service))

        self.assertFalse(result['status'])
        self.assertEqual(result['data'], 'No active accounts found')
        self.mock_account_service.get_active_accounts.assert_called_once()
        self.mock_trading_service.calculate_lot_size.assert_not_called()
        self.mock_trading_service.place_order.assert_not_called()

if __name__ == '__main__':
    unittest.main()