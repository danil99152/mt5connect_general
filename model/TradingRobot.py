"""The TradingRobot class contains the logic for running a trading robot"""


class TradingRobot:
    def __init__(self):
        self.send_retcodes = {
            -800: ('CUSTOM_RETCODE_NOT_ENOUGH_MARGIN', 'Уменьшите множитель или увеличьте сумму инвестиции'),
            -700: ('CUSTOM_RETCODE_LIMITS_NOT_CHANGED', 'Уровни не изменены'),
            # ... and so on
        }

    def run(self):
        # your code to run the trading robot goes here
        pass
