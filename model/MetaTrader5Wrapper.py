""""The MetaTrader5Wrapper class contains methods for connecting to the Metatrader5 API,
getting market data, managing orders, and so on.
"""

import json
from datetime import datetime, timedelta

import MetaTrader5 as Mt
import requests

import settings


class MetaTrader5Wrapper:
    __slots__ = []

    @staticmethod
    def init_mt(init_data):
        """Инициализация терминала"""
        res = Mt.initialize(login=init_data['login'], server=init_data['server'], password=init_data['password'],
                            path=init_data['terminal_path'], timeout=settings.TIMEOUT_INIT, port=8223)
        return res

    @staticmethod
    def get_account_info():
        return Mt.account_info()

    @staticmethod
    def get_positions():
        return Mt.positions_get()

    @staticmethod
    async def patching_quotes():
        utc_to = datetime.combine(datetime.today(), datetime.min.time())
        utc_from = utc_to - timedelta(days=1)
        quotes = ['EURUSD', 'USDRUB', 'EURRUB']
        for i, quote in enumerate(quotes):
            i = i + 1
            try:
                if quote == 'EURRUB':
                    eurusd = Mt.copy_rates_range("EURUSD", Mt.TIMEFRAME_H4, utc_from, utc_to)[-1][4]
                    usdrub = Mt.copy_rates_range("USDRUB", Mt.TIMEFRAME_H4, utc_from, utc_to)[-1][4]
                    data = {"currencies": quote,
                            "close": eurusd * usdrub}
                else:
                    data = {"currencies": quote,
                            "close": Mt.copy_rates_range(quote, Mt.TIMEFRAME_H4, utc_from, utc_to)[-1][4]}
                payload = json.dumps(data,
                                     sort_keys=True,
                                     indent=1)
                headers = {'Content-Type': 'application/json'}
                patch_url = settings.host + f'update/{i}/'
                requests.request("PATCH", patch_url, headers=headers, data=payload)
            except Exception as e:
                print("Exception in patching_quotes:", e)

    @staticmethod
    def get_symbol_info_tick(symbol):
        return Mt.symbol_info_tick(symbol)

    @staticmethod
    def get_symbol_info(symbol):
        return Mt.symbol_info(symbol)

    @staticmethod
    def get_trade_action_deal():
        return Mt.TRADE_ACTION_DEAL

    @staticmethod
    def get_order_filling_fok():
        return Mt.get_ORDER_FILLING_FOK

    @staticmethod
    def get_order_type_buy():
        return Mt.ORDER_TYPE_BUY

    @staticmethod
    def get_order_type_sell():
        return Mt.ORDER_TYPE_SELL

    @staticmethod
    def get_position_type_sell():
        return Mt.POSITION_TYPE_SELL

    @staticmethod
    def get_position_type_buy():
        return Mt.POSITION_TYPE_BUY

    @staticmethod
    def get_order_time_gtc():
        return Mt.ORDER_TIME_GTC

    @staticmethod
    def get_order_filling_ioc():
        return Mt.ORDER_FILLING_IOC

    @staticmethod
    def order_send(request):
        Mt.order_send(request)

    @staticmethod
    def get_history_deals_get_with_date(date_from=datetime(1970, 1, 1), date_to=datetime.now()):
        return Mt.history_deals_get(date_from, date_to)

    @staticmethod
    def get_history_deals_get_with_pos_id(position_id):
        return Mt.history_deals_get(position_id)

    @staticmethod
    def get_trade_action_sltp():
        return Mt.TRADE_ACTION_SLTP

    @staticmethod
    def get_balance():
        return Mt.account_info().balance

    @staticmethod
    def order_check(request):
        return Mt.order_check(request)
