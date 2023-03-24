"""The TradingRobot class contains the logic for running a trading robot"""
import asyncio
from math import fabs, floor
from datetime import datetime, timedelta

import aiohttp
import requests

import settings
from model.DealComment import DealComment
from model.LinkedPositions import LinkedPositions


class TradingRobot:
    __slots__ = ['deal_comment', 'lieder_positions',
                 'investors_disconnect_store', 'source',
                 'lieder_existed_position_tickets', 'start_date_utc',
                 'lieder_balance', 'lieder_equity', 'input_positions',
                 'EURUSD', 'USDRUB', 'EURRUB', 'trading_event', 'event_loop']

    def __init__(self):
        self.deal_comment = DealComment()
        self.lieder_positions = []
        self.investors_disconnect_store = [[], []]
        self.source = settings.source
        self.lieder_existed_position_tickets = settings.lieder_existed_position_tickets
        self.start_date_utc = settings.start_date_utc

        self.lieder_balance = settings.lieder_balance
        self.lieder_equity = settings.lieder_equity
        self.input_positions = settings.lieder_positions

        self.EURUSD = self.USDRUB = self.EURRUB = -1

        self.trading_event = asyncio.Event()
        self.event_loop = asyncio.new_event_loop()

    async def update_setup(self):
        while True:
            await self.source_setup()
            await asyncio.sleep(.5)

    async def source_setup(self):
        main_source = {}
        url = settings.host + 'last'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as get_response:
                    response = await get_response.json()  # .text()
        except Exception as e:
            print(e)
            response = []
        if len(response) > 0:
            response = response[0]
            main_source['lieder'] = {
                'address': r'http://localhost:8000/investor/',
                'login': int(response['leader_login']),
                'password': response['leader_password'],
                'server': response['leader_server']
            }
            main_source['investors'] = [
                {
                    'address': r'http://localhost:8001/investor/',
                    'login': int(response['investor_one_login']),
                    'password': response['investor_one_password'],
                    'server': response['investor_one_server'],
                    'investment_size': float(response['investment_one_size']),
                    'dcs_access': response['access_1'],

                    "deal_in_plus": float(response['deal_in_plus']),
                    "deal_in_minus": float(response['deal_in_minus']),
                    "waiting_time": int(response['waiting_time']),
                    "ask_an_investor": response['ask_an_investor'],
                    "price_refund": response['price_refund'],
                    "multiplier": response['multiplier'],
                    "multiplier_value": float(response['multiplier_value']),
                    "changing_multiplier": response['changing_multiplier'],
                    "stop_loss": response['stop_loss'],
                    "stop_value": float(response['stop_value']),
                    "open_trades": response['open_trades'],
                    "shutdown_initiator": response['shutdown_initiator'],
                    "disconnect": response['disconnect'],
                    "open_trades_disconnect": response['open_trades_disconnect'],
                    "notification": response['notification'],
                    "blacklist": response['blacklist'],
                    "accompany_transactions": response['accompany_transactions'],
                    "no_exchange_connection": response['no_exchange_connection'],
                    "api_key_expired": response['api_key_expired'],
                    "closed_deals_myself": response['closed_deals_myself'],
                    "reconnected": response['reconnected'],
                    "recovery_model": response['recovery_model'],
                    "buy_hold_model": response['buy_hold_model'],
                    "not_enough_margin": response['not_enough_margin'],
                    "accounts_in_diff_curr": response['accounts_in_diff_curr'],
                    "synchronize_deals": response['synchronize_deals'],
                    "deals_not_opened": response['deals_not_opened'],
                    "closed_deal_investor": response['closed_deal_investor'],
                    "opening_deal": response['opening_deal'],
                    "closing_deal": response['closing_deal'],
                    "target_and_stop": response['target_and_stop'],
                    "signal_relevance": response['signal_relevance'],
                    "profitability": response['profitability'],
                    "risk": response['risk'],
                    "profit": response['profit'],
                    "comment": response['comment'],
                },
                {
                    'address': r'http://localhost:8002/investor/',
                    'login': int(response['investor_two_login']),
                    'password': response['investor_two_password'],
                    'server': response['investor_two_server'],
                    'investment_size': float(response['investment_two_size']),
                    'dcs_access': response['access_2'],

                    "deal_in_plus": float(response['deal_in_plus']),
                    "deal_in_minus": float(response['deal_in_minus']),
                    "waiting_time": int(response['waiting_time']),
                    "ask_an_investor": response['ask_an_investor'],
                    "price_refund": response['price_refund'],
                    "multiplier": response['multiplier'],
                    "multiplier_value": float(response['multiplier_value']),
                    "changing_multiplier": response['changing_multiplier'],
                    "stop_loss": response['stop_loss'],
                    "stop_value": float(response['stop_value']),
                    "open_trades": response['open_trades'],
                    "shutdown_initiator": response['shutdown_initiator'],
                    "disconnect": response['disconnect'],
                    "open_trades_disconnect": response['open_trades_disconnect'],
                    "notification": response['notification'],
                    "blacklist": response['blacklist'],
                    "accompany_transactions": response['accompany_transactions'],
                    "no_exchange_connection": response['no_exchange_connection'],
                    "api_key_expired": response['api_key_expired'],
                    "closed_deals_myself": response['closed_deals_myself'],
                    "reconnected": response['reconnected'],
                    "recovery_model": response['recovery_model'],
                    "buy_hold_model": response['buy_hold_model'],
                    "not_enough_margin": response['not_enough_margin'],
                    "accounts_in_diff_curr": response['accounts_in_diff_curr'],
                    "synchronize_deals": response['synchronize_deals'],
                    "deals_not_opened": response['deals_not_opened'],
                    "closed_deal_investor": response['closed_deal_investor'],
                    "opening_deal": response['opening_deal'],
                    "closing_deal": response['closing_deal'],
                    "target_and_stop": response['target_and_stop'],
                    "signal_relevance": response['signal_relevance'],
                    "profitability": response['profitability'],
                    "risk": response['risk'],
                    "profit": response['profit'],
                    "comment": response['comment'],
                }
            ]
            main_source['settings'] = {
                "relevance": response['relevance'],
                "update_at": response['update_at'],
                "created_at": response['created_at']
            }
            prev_date = main_source['settings']['created_at'].split('.')
            self.start_date_utc = datetime.strptime(prev_date[0], "%Y-%m-%dT%H:%M:%S")

            requests.post(url=main_source['lieder']['address'] + 'init/',
                          json=main_source['lieder'])

            inf = dict(requests.get(url=main_source['lieder']['address'] + 'get-account-info/'))

            main_source['lieder']['currency'] = inf.get('currency') if inf else '-'
            for _ in main_source['investors']:
                try:
                    idx = main_source['investors'].index(_)
                    requests.post(url=main_source['investors'][idx]['address'] + 'init/',
                                  json=main_source['investors'][idx])

                    inf = dict(requests.get(url=main_source['investors'][idx]['address'] + 'get-account-info/'))
                    main_source['investors'][idx]['currency'] = inf.get('currency') if inf else '-'
                except Exception as e:
                    print("Request init mt5:", e)
        else:
            self.lieder_existed_position_tickets = []
        self.source = main_source.copy()

    def store_change_disconnect_state(self):
        if len(self.source) > 0:
            for investor in self.source['investors']:
                index = self.source['investors'].index(investor)
                # print('---------------------', index, investor['disconnect'])
                if len(self.investors_disconnect_store[index]) == 0 or \
                        investor['disconnect'] != self.investors_disconnect_store[index][-1]:
                    self.investors_disconnect_store[index].append(investor['disconnect'])

    @staticmethod
    async def set_comment(comment):
        if not settings.send_messages:
            return
        if not comment or comment == 'None':
            return
        async with aiohttp.ClientSession() as session:
            url = settings.host + 'last'
            rsp = requests.get(url)
            if not rsp:
                return
            response = rsp.json()[0]
            numb = response['id']
            url = settings.host + f'patch/{numb}/'
            async with session.patch(url=url, data={"comment": comment}) as resp:
                await resp.json()

    async def update_lieder_info(self, sleep=settings.sleep_lieder_update):
        while True:
            if len(self.source) > 0:
                init_res = requests.post(url=self.source['lieder']['address'] + 'init/',
                                         json=self.source['lieder'])

                if not init_res:
                    await self.set_comment('Ошибка инициализации лидера')
                    await asyncio.sleep(sleep)
                    continue
                get_account_info = dict(requests.get(url=self.source['lieder']['address'] + 'get-account-info/'))
                self.lieder_balance = get_account_info.get('balance')
                self.lieder_equity = get_account_info.get('equity')
                self.input_positions = dict(requests.get(url=self.source['lieder']['address'] + 'get-positions/'))

                if len(self.lieder_existed_position_tickets) == 0:
                    for _ in self.input_positions:
                        self.lieder_existed_position_tickets.append(_.ticket)

                self.lieder_positions = []
                if self.source['investors'][0]['reconnected'] == 'Не переоткрывать':
                    for _ in self.input_positions:
                        if _.ticket not in self.lieder_existed_position_tickets:
                            self.lieder_positions.append(_)
                else:
                    if len(self.lieder_existed_position_tickets) > 0:
                        self.lieder_existed_position_tickets = []
                    self.lieder_positions = self.input_positions

                self.store_change_disconnect_state()  # сохранение Отключился в список
                print(
                    f'\nLIEDER {self.source["lieder"]["login"]} [{self.source["lieder"]["currency"]}] - '
                    f'{len(self.lieder_positions)} positions :',
                    datetime.utcnow().replace(microsecond=0),
                    ' [EURUSD', self.EURUSD, ': USDRUB', self.USDRUB, ': EURRUB', str(round(self.EURRUB, 3)) + ']',
                    ' Comments:', settings.send_messages)
                self.trading_event.set()
            await asyncio.sleep(sleep)

    def get_disconnect_change(self, investor):
        result = None
        idx = -1
        for _ in self.source['investors']:
            if _['login'] == investor['login']:
                idx = self.source['investors'].index(_)
        if idx > -1:
            if self.investors_disconnect_store[idx][-1] == 'Да':
                result = 'Disabled'
            elif self.investors_disconnect_store[idx][-1] == 'Нет':
                result = 'Enabled'
        if len(self.investors_disconnect_store[idx]) <= 1:
            result = 'Unchanged'
        # print(investors_disconnect_store)
        return result

    async def disable_dcs(self, investor):
        if not settings.send_messages:
            return
        async with aiohttp.ClientSession() as session:
            investor_id = -1
            for _ in self.source['investors']:
                if _['login'] == investor['login']:
                    investor_id = self.source['investors'].index(_)
                    break
            if investor_id < 0:
                return
            id_shift = '_' + str(investor_id + 1)
            url = settings.host + 'last'
            response = requests.get(url).json()[0]
            numb = response['id']
            url = settings.host + f'patch/{numb}/'
            name = "access" + id_shift
            async with session.patch(url=url, data={name: False}) as resp:
                await resp.json()

    async def enable_dcs(self, investor):
        if not settings.send_messages:
            return
        async with aiohttp.ClientSession() as session:
            investor_id = -1
            for _ in self.source['investors']:
                if _['login'] == investor['login']:
                    investor_id = self.source['investors'].index(_)
                    break
            if investor_id < 0:
                return
            id_shift = '_' + str(investor_id + 1)
            url = settings.host + 'last'
            response = requests.get(url).json()[0]
            numb = response['id']
            url = settings.host + f'patch/{numb}/'
            name = "access" + id_shift
            async with session.patch(url=url, data={name: True}) as resp:
                await resp.json()

    async def access_starter(self, investor):
        # print(get_disconnect_change(investor))
        if not investor['dcs_access'] and self.get_disconnect_change(investor) == 'Enabled':
            await self.enable_dcs(investor)

    async def check_notification(self, investor):
        if investor['notification'] == 'Да':
            await self.set_comment('Вы должны оплатить вознаграждение')
            return True
        return False

    async def check_connection_exchange(self, investor):
        close_reason = None
        try:
            if investor['api_key_expired'] == "Да":
                close_reason = '04'
                # force_close_all_positions(investor=investor, reason=close_reason)
            elif investor['no_exchange_connection'] == 'Да':
                close_reason = '05'
                # force_close_all_positions(investor=investor, reason=close_reason)
            if close_reason:
                await self.set_comment(comment=settings.reasons_code[close_reason])
        except Exception as e:
            print("Exception in patching_connection_exchange:", e)
        return True if close_reason else False

    @staticmethod
    async def disable_synchronize(exe_flag=False):
        if not settings.send_messages or not exe_flag:
            return
        async with aiohttp.ClientSession() as session:
            url = settings.host + 'last'
            answer = requests.get(url).json()
            if not answer or len(answer) == 0:
                return
            response = answer[0]
            numb = response['id']
            url = settings.host + f'patch/{numb}/'
            async with session.patch(url=url, data={"synchronize_deals": 'Нет'}) as resp:
                await resp.json()

    def get_investor_positions(self, address, only_own=True):
        """Количество открытых позиций"""
        result = []
        if len(self.source) > 0:
            try:
                positions = requests.get(url=address + 'get-positions/')
            except:
                positions = False
            if not positions:
                positions = []
            if only_own and len(positions) > 0:
                for _ in positions:
                    if positions[positions.index(_)].magic == settings.MAGIC and self.deal_comment.is_valid_string(
                            _.comment):
                        result.append(_)
            else:
                result = positions
        return result

    def get_investors_positions_count(self, investor, only_own=True):
        """Количество открытых позиций"""
        return len(self.get_investor_positions(address=investor['address'])) if only_own \
            else len(self.get_investor_positions(address=investor['address'], only_own=False))

    def close_position(self, investor, position, reason):
        """Закрытие указанной позиции"""
        requests.post(url=investor['address'] + 'init/',
                      json=investor)
        tick = dict(requests.get(url=investor['address'] + 'get-symbol-info-tick', params={'symbol': position.symbol}))
        if not tick:
            return
        new_comment_str = position.comment
        if DealComment.is_valid_string(position.comment):
            comment = DealComment().set_from_string(position.comment)
            comment.reason = reason
            new_comment_str = comment.string()
        request = {
            'action': requests.get(investor['address'] + 'get-trade-action-deal/'),
            'position': position.ticket,
            'symbol': position.symbol,
            'volume': position.volume,
            'type': requests.get(investor['address'] + 'get-order-type-buy/') if position.type == 1
            else requests.get(investor['address'] + 'get-order-type-sell/'),
            'price': tick.get('ask') if position.type == 1 else tick.get('bid'),
            'deviation': settings.DEVIATION,
            'magic:': settings.MAGIC,
            'comment': new_comment_str,
            'type_tim': requests.get(investor['address'] + 'get-order-time-gtc/'),
            'type_filing': requests.get(investor['address'] + 'get-order-filling-ioc/'),
        }
        result = requests.post(url=investor['address'] + 'order-send/', data=request)
        return result

    def force_close_all_positions(self, investor, reason):
        """Принудительное закрытие всех позиций аккаунта"""
        init_res = requests.post(url=investor['address'] + 'init/',
                                 json=investor)
        if init_res:
            positions = self.get_investor_positions(address=investor['address'], only_own=False)
            if len(positions) > 0:
                for position in positions:
                    if position.magic == settings.MAGIC and DealComment.is_valid_string(position.comment):
                        self.close_position(investor, position, reason=reason)

    async def execute_conditions(self, investor):
        if investor['disconnect'] == 'Да':
            await self.set_comment('Инициатор отключения: ' + investor['shutdown_initiator'])

            if self.get_investors_positions_count(investor=investor, only_own=True) == 0:  # если нет открытых сделок
                await self.disable_dcs(investor)

            if investor['open_trades_disconnect'] == 'Закрыть':  # если сделки закрыть
                self.force_close_all_positions(investor, reason='03')
                await self.disable_dcs(investor)

            elif investor['accompany_transactions'] == 'Нет':  # если сделки оставить и не сопровождать
                await self.disable_dcs(investor)

    def get_history_profit(self, address):
        """Расчет прибыли по истории"""
        date_from = self.start_date_utc + settings.SERVER_DELTA_TIME
        date_to = datetime.now().replace(microsecond=0) + timedelta(days=1)
        deals = requests.get(url=address + 'get-history-deals-get-with-date/', params={'date_from': date_from,
                                                                                       'date_to': date_to})

        if not deals:
            deals = []
        result = 0
        own_deals = []
        try:
            pos_tickets = []
            if len(deals) > 0:
                for pos in deals:
                    if DealComment.is_valid_string(pos.comment):
                        linked_pos = dict(requests.get(url=address + 'get-history-deals-get-with-pos-id/',
                                                       params={'position_id': pos.position_id}))
                        for lp in linked_pos:
                            if lp.ticket not in pos_tickets:
                                # print(linked_pos.index(lp), datetime.utcfromtimestamp(lp.time), ' ', lp.ticket, ' ',
                                #       lp.profit)
                                pos_tickets.append(lp.ticket)
                                own_deals.append(lp)
            if len(own_deals) > 0:
                for pos in own_deals:
                    # print(datetime.utcfromtimestamp(pos.time), ' ', pos.ticket, ' ', pos.profit)
                    if pos.type < 2:
                        result += pos.profit  # + pos.commission
        except Exception as ex:
            print('ERROR get_history_profit():', ex)
            result = None
        return result

    def get_positions_profit(self, address):
        """Расчет прибыли текущих позиций"""
        positions = self.get_investor_positions(address=address, only_own=True)
        result = 0
        if len(positions) > 0:
            for pos in positions:
                if pos.type < 2:
                    result += pos.profit  # + pos.commission
        return result

    async def check_stop_limits(self, investor):
        """Проверка стоп-лимита по проценту либо абсолютному показателю"""
        start_balance = investor['investment_size']
        if start_balance <= 0:
            start_balance = 1
        limit_size = investor['stop_value']
        calc_limit_in_percent = True if investor['stop_loss'] == 'Процент' else False
        requests.post(url=investor['address'] + 'init/',
                      json=investor)
        history_profit = self.get_history_profit(address=investor['address'])
        current_profit = self.get_positions_profit(investor['address'])
        # SUMM TOTAL PROFIT
        if history_profit is None or current_profit is None:
            return
        close_positions = False
        total_profit = history_profit + current_profit
        print(
            f' - {investor["login"]} [{investor["currency"]}]'
            f' - {len(list(requests.get(investor["address"] + "get-positions/")))} positions. Access:',
            investor['dcs_access'], end='')
        print('\t', 'Прибыль' if total_profit >= 0 else 'Убыток', 'торговли c', self.start_date_utc,
              ':', round(total_profit, 2), investor['currency'],
              '{curr.', round(current_profit, 2), ': hst. ' + str(round(history_profit, 2)) + '}')
        # CHECK LOST SIZE FOR CLOSE ALL
        if total_profit < 0:
            if calc_limit_in_percent:
                current_percent = fabs(total_profit / start_balance) * 100
                if current_percent >= limit_size:
                    close_positions = True
            elif fabs(total_profit) >= limit_size:
                close_positions = True
            # CLOSE ALL POSITIONS
            active_positions = self.get_investor_positions(address=investor['address'])
            if close_positions and len(active_positions) > 0:
                print('     Закрытие всех позиций по условию стоп-лосс')
                await self.set_comment('Закрытие всех позиций по условию стоп-лосс. Убыток торговли c' + str(
                    self.start_date_utc.replace(microsecond=0)) + ':' + str(round(total_profit, 2)))
                for act_pos in active_positions:
                    if act_pos.magic == settings.MAGIC:
                        self.close_position(investor, act_pos, '07')
                if investor['open_trades'] == 'Закрыть и отключить':
                    await self.disable_dcs(investor)

    def synchronize_positions_volume(self, investor):
        try:
            investors_balance = investor['investment_size']
            login = investor.get("login")
            if login not in settings.old_investors_balance:
                settings.old_investors_balance[login] = investors_balance
            if "Корректировать объем" in (investor["recovery_model"], investor["buy_hold_model"]):
                if investors_balance != settings.old_investors_balance[login]:
                    volume_change_coefficient = investors_balance / settings.old_investors_balance[login]
                    if volume_change_coefficient != 1.0:
                        requests.post(url=investor['address'] + 'init/',
                                      json=investor)
                        investors_positions_table = LinkedPositions.get_linked_positions_table(
                            self.get_investor_positions(address=investor['address']))
                        for _ in investors_positions_table:
                            min_lot = dict(requests.get(investor['address'] + 'get-symbol-info/',
                                                        params={'symbol': _.symbol})).get('volume_min')
                            decimals = str(min_lot)[::-1].find('.')
                            volume = _.volume
                            new_volume = round(volume_change_coefficient * volume, decimals)
                            if volume != new_volume:
                                _.modify_volume(new_volume)
                    settings.old_investors_balance[login] = investors_balance
        except Exception as e:
            print("Exception in synchronize_positions_volume():", e)

    @staticmethod
    def get_pos_pips_tp(address, position, price=None):
        """Расчет Тейк-профит в пунктах"""
        if price is None:
            price = position.price_open
        result = 0.0
        if position.tp > 0:
            result = round(
                fabs(price - position.tp) / dict(requests.get(url=address, params={"symbol": position.symbol})).get(
                    'point'))
        return result

    @staticmethod
    def get_pos_pips_sl(address, position, price=None):
        """Расчет Стоп-лосс в пунктах"""
        if price is None:
            price = position.price_open
        result = 0.0
        if position.sl > 0:
            result = round(
                fabs(price - position.sl) / dict(requests.get(url=address, params={"symbol": position.symbol})).get(
                    'point'))
        return result

    def synchronize_positions_limits(self, investor):
        """Изменение уровней ТП и СЛ указанной позиции"""
        requests.post(url=investor['address'] + 'init/',
                      json=investor)
        for l_pos in self.lieder_positions:
            l_tp = self.get_pos_pips_tp(address=investor['address'], position=l_pos)
            l_sl = self.get_pos_pips_sl(address=investor['address'], position=l_pos)
            if l_tp > 0 or l_sl > 0:
                for i_pos in self.get_investor_positions(address=investor['address']):
                    request = []
                    new_comment_str = comment = ''
                    if DealComment.is_valid_string(i_pos.comment):
                        comment = DealComment().set_from_string(i_pos.comment)
                        comment.reason = '09'
                        new_comment_str = comment.string()
                    if comment.lieder_ticket == l_pos.ticket:
                        i_tp = self.get_pos_pips_tp(address=investor['address'], position=i_pos)
                        i_sl = self.get_pos_pips_sl(address=investor['address'], position=i_pos)
                        sl_lvl = tp_lvl = 0.0
                        if i_pos.type == self.mt5wrapper.get_order_type_buy():
                            sl_lvl = i_pos.price_open - l_sl * self.mt5wrapper.get_symbol_info(i_pos.symbol).point
                            tp_lvl = i_pos.price_open + l_tp * self.mt5wrapper.get_symbol_info(i_pos.symbol).point
                        elif i_pos.type == self.mt5wrapper.get_order_type_sell():
                            sl_lvl = i_pos.price_open + l_sl * self.mt5wrapper.get_symbol_info(i_pos.symbol).point
                            tp_lvl = i_pos.price_open - l_tp * self.mt5wrapper.get_symbol_info(i_pos.symbol).point
                        if i_tp != l_tp or i_sl != l_sl:
                            request = {
                                "action": self.mt5wrapper.get_trade_action_sltp(),
                                "position": i_pos.ticket,
                                "symbol": i_pos.symbol,
                                "sl": sl_lvl,
                                "tp": tp_lvl,
                                "magic": settings.MAGIC,
                                "comment": new_comment_str
                            }
                    if request:
                        result = self.mt5wrapper.order_send(request)
                        print('Лимит изменен:', result)

    def is_lieder_position_in_investor(self, investor_address, lieder_position):
        invest_positions = self.get_investor_positions(address=investor_address, only_own=False)
        if len(invest_positions) > 0:
            for pos in invest_positions:
                if DealComment.is_valid_string(pos.comment):
                    comment = DealComment().set_from_string(pos.comment)
                    if lieder_position.ticket == comment.lieder_ticket:
                        return True
        return False

    def is_lieder_position_in_investor_history(self, lieder_position):
        date_from = self.start_date_utc + settings.SERVER_DELTA_TIME
        date_to = datetime.today().replace(microsecond=0) + timedelta(days=1)
        deals = self.mt5wrapper.get_history_deals_get_with_date(date_from, date_to)
        if not deals:
            deals = []
        result = None
        result_sl = None
        if len(deals) > 0:
            for pos in deals:
                if DealComment.is_valid_string(pos.comment):
                    comment = DealComment().set_from_string(pos.comment)
                    if lieder_position.ticket == comment.lieder_ticket:
                        result = pos
                        if comment.reason == '07':
                            result_sl = pos
                if result and result_sl:
                    break
        return result, result_sl

    def is_position_opened(self, lieder_position, investor):
        """Проверка позиции лидера на наличие в списке позиций и истории инвестора"""
        requests.post(url=investor['address'] + 'init/',
                      json=investor)
        if self.is_lieder_position_in_investor(investor_address=investor['address'], lieder_position=lieder_position):
            return True

        exist_position, closed_by_sl = self.is_lieder_position_in_investor_history(lieder_position=lieder_position)
        if exist_position:
            if not closed_by_sl:
                if investor['closed_deals_myself'] == 'Переоткрывать':
                    return False
            return True
        return False

    @staticmethod
    def check_transaction(investor, lieder_position):
        """Проверка открытия позиции"""
        price_refund = True if investor['price_refund'] == 'Да' else False
        if not price_refund:  # если не возврат цены
            timeout = investor['waiting_time'] * 60
            deal_time = int(lieder_position.time_update - datetime.utcnow().timestamp())  # get_time_offset(investor))
            curr_time = int(datetime.timestamp(datetime.utcnow().replace(microsecond=0)))
            delta_time = curr_time - deal_time
            if delta_time > timeout:  # если время больше заданного
                return False

    def multiply_deal_volume(self, investor, lieder_position):
        """Расчет множителя"""
        lieder_balance_value = self.lieder_balance if investor['multiplier'] == 'Баланс' else self.lieder_equity
        symbol = lieder_position.symbol
        lieder_volume = lieder_position.volume
        multiplier = investor['multiplier_value']
        investment_size = investor['investment_size']
        get_for_balance = True if investor['multiplier'] == 'Баланс' else False
        if get_for_balance:
            ext_k = (investment_size + self.get_history_profit(address=investor['address'])) / lieder_balance_value
        else:
            ext_k = (investment_size + self.get_history_profit(address=investor['address']) + self.get_positions_profit(
                investor['address'])) / lieder_balance_value
        try:
            min_lot = self.mt5wrapper.get_symbol_info(symbol).volume_min
            decimals = str(min_lot)[::-1].find('.')
        except AttributeError:
            decimals = 2
        if investor['changing_multiplier'] == 'Нет':
            result = round(lieder_volume * ext_k, decimals)
        else:
            result = round(lieder_volume * multiplier * ext_k, decimals)
        return result

    def close_positions_by_lieder(self, investor):
        """Закрытие позиций инвестора, которые закрылись у лидера"""
        requests.post(url=investor['address'] + 'init/',
                      json=investor)
        positions_investor = self.get_investor_positions(address=investor['address'])
        non_existed_positions = []
        if positions_investor:
            for ip in positions_investor:
                position_exist = False
                for lp in self.lieder_positions:
                    comment = DealComment().set_from_string(ip.comment)
                    if comment.lieder_ticket == lp.ticket:
                        position_exist = True
                        break
                if not position_exist:
                    non_existed_positions.append(ip)
        for pos in non_existed_positions:
            print('     close position:', pos.comment)
            self.close_position(investor, pos, reason='06')

    def get_currency_coefficient(self, investor):
        lid_currency = self.source['lieder']['currency']
        inv_currency = investor['currency']
        eurusd = usdrub = eurrub = -1

        rub_tick = self.mt5wrapper.get_symbol_info_tick('USDRUB')
        if rub_tick:
            usdrub = rub_tick.bid
        eur_tick = self.mt5wrapper.get_symbol_info_tick('EURUSD')
        if eur_tick:
            eurusd = eur_tick.bid
        if rub_tick and eur_tick:
            eurrub = usdrub * eurusd
        if eurusd > 0:
            self.EURUSD = eurusd
        if usdrub > 0:
            self.USDRUB = usdrub
        if eurrub > 0:
            self.EURRUB = eurrub
        currency_coefficient = 1
        try:
            if lid_currency == inv_currency:
                currency_coefficient = 1
            elif lid_currency == 'USD':
                if inv_currency == 'EUR':
                    currency_coefficient = 1 / eurusd
                elif inv_currency == 'RUB':
                    currency_coefficient = usdrub
            elif lid_currency == 'EUR':
                if inv_currency == 'USD':
                    currency_coefficient = eurusd
                elif inv_currency == 'RUB':
                    currency_coefficient = eurrub
            elif lid_currency == 'RUB':
                if inv_currency == 'USD':
                    currency_coefficient = 1 / usdrub
                elif inv_currency == 'EUR':
                    currency_coefficient = 1 / eurrub
        except Exception as e:
            print('Except in get_currency_coefficient()', e)
            currency_coefficient = 1
        return currency_coefficient

    def get_lots_for_investment(self, address, symbol, investment):
        print(
            f'\nsymbol: {symbol}')  # currency_base: {Mt.symbol_info(smb).currency_base}  currency_profit: {Mt.symbol_info(smb).currency_profit}  currency_margin: {Mt.symbol_info(smb).currency_margin}')
        price = self.mt5wrapper.get_symbol_info_tick(symbol).bid
        leverage = dict(requests.get(url=address + 'get-account-info/')).get('leverage')
        contract = self.mt5wrapper.get_symbol_info(symbol).trade_contract_size

        min_lot = self.mt5wrapper.get_symbol_info(symbol).volume_min
        lot_step = self.mt5wrapper.get_symbol_info(symbol).volume_step
        decimals = str(lot_step)[::-1].find('.')

        volume_none_round = (investment * leverage) / (contract * price)
        if volume_none_round < min_lot:
            volume = 0.0
        else:
            volume = round(floor(volume_none_round / lot_step) * lot_step, decimals)

        print(
            f'Размер инвестиции: {investment}  Курс: {price}  Контракт: {contract}  Плечо: {leverage}  >>  ОБЪЕМ: {volume}')

        return volume

    async def edit_volume_for_margin(self, investor, request):
        """Расчет объема при недостатке маржи и проверка на максимальный"""
        requests.post(url=investor['address'] + 'init/',
                      json=investor)

        response = self.mt5wrapper.order_check(request)
        if not response or len(response) <= 0:
            return 'EMPTY_REQUEST'
        if response.retcode == 10019 or response.retcode == 10014:  # Неправильный объем # Нет достаточных денежных средств для выполнения запроса
            info = self.mt5wrapper.get_symbol_info(request['symbol'])
            max_vol = info.volume_max
            # min_vol = info.volume_min
            if request['volume'] > max_vol:
                print(investor['login'], f'Объем сделки [{request["volume"]}] больше максимального [{max_vol}]. ')
                await self.set_comment('Объем сделки больше максимального')
                return 'MORE_THAN_MAX_VOLUME'
            if investor['not_enough_margin'] == 'Минимальный объем':
                request['volume'] = self.mt5wrapper.get_symbol_info(request['symbol']).volume_min
            elif investor['not_enough_margin'] == 'Достаточный объем':
                hst_profit = self.get_history_profit(address=investor['address'])
                cur_profit = self.get_positions_profit(investor['address'])
                balance = investor['investment_size'] + hst_profit + cur_profit
                volume = self.get_lots_for_investment(address=investor['address'],
                                                      symbol=request['symbol'],
                                                      investment=balance)
                request['volume'] = volume
            elif investor['not_enough_margin'] == 'Не открывать' \
                    or investor['not_enough_margin'] == 'Не выбрано':
                request = None
        return request

    async def open_position(self, investor, symbol, deal_type, lot, sender_ticket: int, tp=0.0, sl=0.0):
        """Открытие позиции"""
        try:
            point = self.mt5wrapper.get_symbol_info(symbol).point
            price = tp_in = sl_in = 0.0
            if deal_type == 0:  # BUY
                deal_type = self.mt5wrapper.get_order_type_buy()
                price = self.mt5wrapper.get_symbol_info_tick(symbol).ask
            if tp != 0:
                tp_in = price + tp * point
            if sl != 0:
                sl_in = price - sl * point
            elif deal_type == 1:  # SELL
                deal_type = self.mt5wrapper.get_order_type_sell()
                price = self.mt5wrapper.get_symbol_info_tick(symbol).bid
                if tp != 0:
                    tp_in = price - tp * point
                if sl != 0:
                    sl_in = price + sl * point
        except AttributeError:
            return {'retcode': -200}
        comment = DealComment()
        comment.lieder_ticket = sender_ticket
        comment.reason = '01'
        request = {
            "action": self.mt5wrapper.get_trade_action_deal(),
            "symbol": symbol,
            "volume": lot,
            "type": deal_type,
            "price": price,
            "sl": sl_in,
            "tp": tp_in,
            "deviation": settings.DEVIATION,
            "magic": settings.MAGIC,
            "comment": comment.string(),
            "type_time": self.mt5wrapper.get_order_time_gtc(),
            "type_filling": self.mt5wrapper.get_order_filling_fok(),
        }
        checked_request = await self.edit_volume_for_margin(investor,
                                                            request)  # Проверка и расчет объема при недостатке маржи
        if not checked_request:
            return {'retcode': -100}
        elif checked_request == -1:
            # await set_comment('Уменьшите множитель или увеличите сумму инвестиции')
            return {'retcode': -800}
        elif checked_request != 'EMPTY_REQUEST' and checked_request != 'MORE_THAN_MAX_VOLUME':
            result = self.mt5wrapper.order_send(checked_request)
            return result

    async def execute_investor(self, investor):
        await self.access_starter(investor)
        if investor['blacklist'] == 'Да':
            print(investor['login'], 'in blacklist')
            return
        if await self.check_notification(investor):
            print(investor['login'], 'not pay - notify')
            return
        if await self.check_connection_exchange(investor):
            print(investor['login'], 'API expired or Broker disconnected')
            return
        synchronize = True if investor['deals_not_opened'] == 'Да' or investor['synchronize_deals'] == 'Да' else False
        if investor['synchronize_deals'] == 'Да':  # если "синхронизировать"
            await self.disable_synchronize(synchronize)
        if not synchronize:
            return

        try:
            init_res = requests.post(url=investor['address'] + 'init/',
                                     json=investor)
        except:
            init_res = False

        if not init_res:
            await self.set_comment('Ошибка инициализации инвестора ' + str(investor['login']))
            return

        if investor['dcs_access']:
            await self.execute_conditions(investor=investor)  # проверка условий кейса закрытия
        if investor['dcs_access']:
            await self.check_stop_limits(investor=investor)  # проверка условий стоп-лосс
        if investor['dcs_access']:

            self.synchronize_positions_volume(investor)  # коррекция объемов позиций
            self.synchronize_positions_limits(investor)  # коррекция лимитов позиций

            for pos_lid in self.lieder_positions:
                inv_tp = self.get_pos_pips_tp(address=investor['address'], position=pos_lid)
                inv_sl = self.get_pos_pips_sl(address=investor['address'], position=pos_lid)
                requests.post(url=investor['address'] + 'init/',
                              json=investor)
                if not self.is_position_opened(pos_lid, investor):
                    ret_code = None
                    if self.check_transaction(investor=investor, lieder_position=pos_lid):
                        volume = self.multiply_deal_volume(investor, lieder_position=pos_lid)

                        min_lot = self.mt5wrapper.get_symbol_info(pos_lid.symbol).volume_min
                        decimals = str(min_lot)[::-1].find('.')
                        volume = round(volume / self.get_currency_coefficient(investor), decimals)
                        response = await self.open_position(investor=investor, symbol=pos_lid.symbol,
                                                            deal_type=pos_lid.type,
                                                            lot=volume, sender_ticket=pos_lid.ticket,
                                                            tp=inv_tp, sl=inv_sl)
                        if response:
                            try:
                                ret_code = response.retcode
                            except AttributeError:
                                ret_code = response['retcode']
                    if ret_code:
                        msg = str(investor['login']) + ' ' + settings.send_retcodes[ret_code][
                            1]  # + ' : ' + str(ret_code)
                        if ret_code != 10009:  # Заявка выполнена
                            await self.set_comment('\t' + msg)
                        print(msg)
            # else:
            #     set_comment('Не выполнено условие +/-')

        # закрытие позиций от лидера
        if (investor['dcs_access'] or  # если сопровождать сделки или доступ есть
                (not investor['dcs_access'] and investor['accompany_transactions'] == 'Да')):
            self.close_positions_by_lieder(investor)

        # Mt.shutdown()

    async def task_manager(self):
        while True:
            await self.trading_event.wait()

            if datetime.now().strftime("%H:%M:%S") == "10:00:00":
                await self.mt5wrapper.patching_quotes()

            if len(self.source) > 0:
                for _ in self.source['investors']:
                    self.event_loop.create_task(self.execute_investor(_))

            self.trading_event.clear()

    def run(self):
        # set_dummy_data()
        self.event_loop.create_task(self.update_setup())  # для теста без сервера закомментировать
        self.event_loop.create_task(self.update_lieder_info())
        self.event_loop.create_task(self.task_manager())
        self.event_loop.run_forever()
