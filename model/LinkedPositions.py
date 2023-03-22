import settings
from model.DealComment import DealComment
from model.MetaTrader5Wrapper import MetaTrader5Wrapper


class LinkedPositions:
    lieder_ticket: int
    positions: list
    volume: float
    symbol: str
    type: int

    __slots__ = ['mt5wrapper', 'lieder_ticket',
                 'positions', 'symbol', 'type', 'volume']

    def __init__(self, lieder_ticket, investor_positions=None):
        self.mt5wrapper = MetaTrader5Wrapper()
        self.lieder_ticket = lieder_ticket
        self.positions = []
        self.symbol = ''
        self.type = -1
        for pos in investor_positions:
            comment = DealComment().set_from_string(pos.comment)
            if comment.lieder_ticket == self.lieder_ticket:
                self.positions.append(pos)
                if self.symbol == '':
                    self.symbol = pos.symbol
                if self.type < 0:
                    self.type = pos.type
        volume = 0.0
        for _ in self.positions:
            volume += _.volume
        min_lot = self.mt5wrapper.get_symbol_info(self.symbol).volume_min
        decimals = str(min_lot)[::-1].find('.')
        self.volume = round(volume, decimals)

    @staticmethod
    def get_positions_lieder_ticket(position):
        """Получение тикета позиции лидера из позиции инвестора"""
        if DealComment.is_valid_string(position.comment):
            comment = DealComment().set_from_string(position.comment)
            return comment.lieder_ticket
        return -1

    @staticmethod
    def get_linked_positions_table(investor_positions):
        """Получение таблицы позиций инвестора, сгруппированных по тикету позиции лидера"""
        stored_ticket = []
        positions_table = []
        for pos in investor_positions:
            lid_ticket = LinkedPositions.get_positions_lieder_ticket(pos)
            if lid_ticket not in stored_ticket:
                stored_ticket.append(lid_ticket)
                linked_positions = LinkedPositions(lieder_ticket=lid_ticket, investor_positions=investor_positions)
                positions_table.append(linked_positions)
        return positions_table

    def string(self):
        result = "\t"
        result += self.symbol + ' ' + str(self.lieder_ticket) + ' ' + str(self.volume) + " " + str(len(self.positions))
        for _ in self.positions:
            result += '\n\t\t' + str(_)
        return result

    def modify_volume(self, new_volume):
        """Изменение объема связанных позиций"""
        print('  Текущий объем:', self.volume, ' Новый:', new_volume)
        min_lot = self.mt5wrapper.get_symbol_info(self.symbol).volume_min
        decimals = str(min_lot)[::-1].find('.')
        new_comment = DealComment()
        new_comment.lieder_ticket = self.lieder_ticket
        new_comment.reason = '08'
        new_comment_str = new_comment.string()
        if new_volume > self.volume:  # Увеличение объема
            vol = round(new_volume - self.volume, decimals)
            print('\t Увеличение объема на', vol)
            request = {
                "action": self.mt5wrapper.get_trade_action_deal(),
                "symbol": self.symbol,
                "volume": vol,
                "type": self.type,
                "price": self.mt5wrapper.get_symbol_info_tick(
                    self.symbol).bid if self.type == self.mt5wrapper.get_position_type_sell()
                else self.mt5wrapper.get_symbol_info_tick(self.symbol).ask,
                "deviation": settings.DEVIATION,
                "magic": settings.MAGIC,
                "comment": new_comment_str,
                "type_time": self.mt5wrapper.get_order_time_gtc(),
                "type_filling": self.mt5wrapper.get_order_filling_fok(),
            }
            result = self.mt5wrapper.order_send(request)
            return result
        elif new_volume < self.volume:  # Уменьшение объема
            target_volume = round(self.volume - new_volume, decimals)
            for pos in reversed(self.positions):
                if pos.volume <= target_volume:  # Если объем позиции меньше либо равен целевому, то закрыть позицию
                    print('\t Уменьшение объема. Закрытие позиции', pos.ticket, ' объем:', pos.volume)
                    request = {
                        'action': self.mt5wrapper.get_trade_action_deal(),
                        'position': pos.ticket,
                        'symbol': pos.symbol,
                        'volume': pos.volume,
                        "type": self.mt5wrapper.get_order_type_sell()
                        if pos.type == self.mt5wrapper.get_order_type_buy()
                        else self.mt5wrapper.get_order_type_buy(),
                        'price': self.mt5wrapper.get_symbol_info_tick(
                            self.symbol).bid if self.type == self.mt5wrapper.get_position_type_sell()
                        else self.mt5wrapper.get_symbol_info_tick(
                            self.symbol).ask,
                        'deviation': settings.DEVIATION,
                        'magic:': settings.MAGIC,
                        'comment': new_comment_str,
                        'type_tim': self.mt5wrapper.get_order_time_gtc(),
                        'type_filing': self.mt5wrapper.get_order_filling_ioc()
                    }
                    result = self.mt5wrapper.order_send(request)
                    print('\t', settings.send_retcodes[result.retcode], ':', result.retcode)
                    target_volume = round(target_volume - pos.volume,
                                          decimals)  # Уменьшить целевой объем на объем закрытой позиции
                elif pos.volume > target_volume:  # Если объем позиции больше целевого, то закрыть часть позиции
                    print('\t Уменьшение объема. Частичное закрытие позиции', pos.ticket, 'объем:', pos.volume,
                          'на', target_volume)
                    request = {
                        "action": self.mt5wrapper.get_trade_action_deal(),
                        "symbol": pos.symbol,
                        "volume": target_volume,
                        "type": self.mt5wrapper.get_order_type_sell()
                        if pos.type == self.mt5wrapper.get_position_type_buy()
                        else self.mt5wrapper.get_order_type_buy(),
                        "position": pos.ticket,
                        'price': self.mt5wrapper.get_symbol_info_tick(
                            self.symbol).bid
                        if self.type == self.mt5wrapper.get_position_type_sell()
                        else self.mt5wrapper.get_symbol_info_tick(
                            self.symbol).ask,
                        "deviation": settings.DEVIATION,
                        "magic": settings.MAGIC,
                        "comment": new_comment_str,
                        'type_tim': self.mt5wrapper.get_order_time_gtc(),
                        "type_filling": self.mt5wrapper.get_order_filling_fok(),
                    }
                    if target_volume > 0:
                        result = self.mt5wrapper.order_send(request)
                        print('\t', settings.send_retcodes[result.retcode], ':', result.retcode)
                    else:
                        print('\t Частичное закрытие объема = 0.0')
                    break
