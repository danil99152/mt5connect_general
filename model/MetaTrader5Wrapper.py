""""The MetaTrader5Wrapper class contains methods for connecting to the Metatrader5 API,
getting market data, managing orders, and so on.
"""


import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from math import fabs, floor
import MetaTrader5 as Mt


class MetaTrader5Wrapper:
    def __init__(self):
        self.Mt = MetaTrader5

    def connect(self):
        # your code to connect to the Metatrader5 API goes here
        pass

    def get_market_data(self, symbol):
        # your code to get market data for a specific symbol goes here
        pass

    def manage_orders(self, orders):
        # your code to manage orders goes here
        pass

    # and so on
