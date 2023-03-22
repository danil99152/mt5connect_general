import asyncio
from datetime import datetime, timedelta

send_retcodes = {
    -800: ('CUSTOM_RETCODE_NOT_ENOUGH_MARGIN', 'Уменьшите множитель или увеличьте сумму инвестиции'),
    -700: ('CUSTOM_RETCODE_LIMITS_NOT_CHANGED', 'Уровни не изменены'),
    -600: ('CUSTOM_RETCODE_POSITION_NOT_MODIFIED', 'Объем сделки не изменен'),
    -500: ('CUSTOM_RETCODE_POSITION_NOT_MODIFIED', 'Объем сделки не изменен'),
    -400: ('CUSTOM_RETCODE_POSITION_NOT_MODIFIED', 'Объем сделки не изменен'),
    -300: ('CUSTOM_RETCODE_EQUAL_VOLUME', 'Новый объем сделки равен существующему'),
    -200: ('CUSTOM_RETCODE_WRONG_SYMBOL', 'Нет такого торгового символа'),
    -100: ('CUSTOM_RETCODE_NOT_ENOUGH_MARGIN', 'Нехватка маржи. Выбран режим - Не открывать сделку или Не выбрано'),
    10004: ('TRADE_RETCODE_REQUOTE', 'Реквота'),
    10006: ('TRADE_RETCODE_REJECT', 'Запрос отклонен'),
    10007: ('TRADE_RETCODE_CANCEL', 'Запрос отменен трейдером'),
    10008: ('TRADE_RETCODE_PLACED', 'Ордер размещен'),
    10009: ('TRADE_RETCODE_DONE', 'Заявка выполнена'),
    10010: ('TRADE_RETCODE_DONE_PARTIAL', 'Заявка выполнена частично'),
    10011: ('TRADE_RETCODE_ERROR', 'Ошибка обработки запроса'),
    10012: ('TRADE_RETCODE_TIMEOUT', 'Запрос отменен по истечению времени'),
    10013: ('TRADE_RETCODE_INVALID', 'Неправильный запрос'),
    10014: ('TRADE_RETCODE_INVALID_VOLUME', 'Неправильный объем в запросе'),
    10015: ('TRADE_RETCODE_INVALID_PRICE', 'Неправильная цена в запросе'),
    10016: ('TRADE_RETCODE_INVALID_STOPS', 'Неправильные стопы в запросе'),
    10017: ('TRADE_RETCODE_TRADE_DISABLED', 'Торговля запрещена'),
    10018: ('TRADE_RETCODE_MARKET_CLOSED', 'Рынок закрыт'),
    10019: ('TRADE_RETCODE_NO_MONEY', 'Нет достаточных денежных средств для выполнения запроса'),
    10020: ('TRADE_RETCODE_PRICE_CHANGED', 'Цены изменились'),
    10021: ('TRADE_RETCODE_PRICE_OFF', 'Отсутствуют котировки для обработки запроса'),
    10022: ('TRADE_RETCODE_INVALID_EXPIRATION', 'Неверная дата истечения ордера в запросе'),
    10023: ('TRADE_RETCODE_ORDER_CHANGED', 'Состояние ордера изменилось'),
    10024: ('TRADE_RETCODE_TOO_MANY_REQUESTS', 'Слишком частые запросы'),
    10025: ('TRADE_RETCODE_NO_CHANGES', 'В запросе нет изменений'),
    10026: ('TRADE_RETCODE_SERVER_DISABLES_AT', 'Автотрейдинг запрещен сервером'),
    10027: ('TRADE_RETCODE_CLIENT_DISABLES_AT', 'Автотрейдинг запрещен клиентским терминалом'),
    10028: ('TRADE_RETCODE_LOCKED', 'Запрос заблокирован для обработки'),
    10029: ('TRADE_RETCODE_FROZEN', 'Ордер или позиция заморожены'),
    10030: ('TRADE_RETCODE_INVALID_FILL', 'Указан неподдерживаемый тип исполнения ордера по остатку'),
    10031: ('TRADE_RETCODE_CONNECTION', 'Нет соединения с торговым сервером'),
    10032: ('TRADE_RETCODE_ONLY_REAL', 'Операция разрешена только для реальных счетов'),
    10033: ('TRADE_RETCODE_LIMIT_ORDERS', 'Достигнут лимит на количество отложенных ордеров'),
    10034: (
        'TRADE_RETCODE_LIMIT_VOLUME', 'Достигнут лимит на объем ордеров и позиций для данного символа'),
    10035: ('TRADE_RETCODE_INVALID_ORDER', 'Неверный или запрещённый тип ордера'),
    10036: ('TRADE_RETCODE_POSITION_CLOSED', 'Позиция с указанным POSITION_IDENTIFIER уже закрыта'),
    10038: ('TRADE_RETCODE_INVALID_CLOSE_VOLUME', 'Закрываемый объем превышает текущий объем позиции'),
    10039: ('TRADE_RETCODE_CLOSE_ORDER_EXIST', 'Для указанной позиции уже есть ордер на закрытие'),
    10040: ('TRADE_RETCODE_LIMIT_POSITIONS',
            'Количество открытых позиций, которое можно одновременно иметь на счете, '
            'может быть ограничено настройками сервера'),
    10041: (
        'TRADE_RETCODE_REJECT_CANCEL',
        'Запрос на активацию отложенного ордера отклонен, а сам ордер отменен'),
    10042: (
        'TRADE_RETCODE_LONG_ONLY',
        'Запрос отклонен, так как на символе установлено правило "Разрешены только '
        'длинные позиции"  (POSITION_TYPE_BUY)'),
    10043: ('TRADE_RETCODE_SHORT_ONLY',
            'Запрос отклонен, так как на символе установлено правило "Разрешены только '
            'короткие позиции" (POSITION_TYPE_SELL)'),
    10044: ('TRADE_RETCODE_CLOSE_ONLY',
            'Запрос отклонен, так как на символе установлено правило "Разрешено только '
            'закрывать существующие позиции"'),
    10045: ('TRADE_RETCODE_FIFO_CLOSE',
            'Запрос отклонен, так как для торгового счета установлено правило "Разрешено '
            'закрывать существующие позиции только по правилу FIFO" ('
            'ACCOUNT_FIFO_CLOSE=true)'),
    10046: (
        'TRADE_RETCODE_HEDGE_PROHIBITED',
        'Запрос отклонен, так как для торгового счета установлено правило '
        '"Запрещено открывать встречные позиции по одному символу"')}
last_errors = {
    1: ('RES_S_OK', 'generic success'),
    -1: ('RES_E_FAIL', 'generic fail'),
    -2: ('RES_E_INVALID_PARAMS', 'invalid arguments/parameters'),
    -3: ('RES_E_NO_MEMORY', 'no memory condition'),
    -4: ('RES_E_NOT_FOUND', 'no history'),
    -5: ('RES_E_INVALID_VERSION', 'invalid version'),
    -6: ('RES_E_AUTH_FAILED', 'authorization failed'),
    -7: ('RES_E_UNSUPPORTED', 'unsupported method'),
    -8: ('RES_E_AUTO_TRADING_DISABLED', 'auto-trading disabled'),
    -10000: ('RES_E_INTERNAL_FAIL', 'internal IPC general error'),
    -10001: ('RES_E_INTERNAL_FAIL_SEND', 'internal IPC send failed'),
    -10002: ('RES_E_INTERNAL_FAIL_RECEIVE', 'internal IPC recv failed'),
    -10003: ('RES_E_INTERNAL_FAIL_INIT', 'internal IPC initialization fail'),
    -10003: ('RES_E_INTERNAL_FAIL_CONNECT', 'internal IPC no ipc'),
    -10005: ('RES_E_INTERNAL_FAIL_TIMEOUT', 'internal timeout')}
reasons_code = {
    '01': 'Открыто СКС',
    '02': 'Блеклист',
    '03': 'Закрыто по команде пользователя',
    '04': 'Ключ APi истек',
    '05': 'Нет связи с биржей',
    '06': 'Закрыто инвестором',
    '07': 'Закрыто по условию стоп-лосс',
    '08': 'Объем изменен',
    '09': 'Лимиты изменены',
}

TIMEOUT_INIT = 60_000  # время ожидания при инициализации терминала (рекомендуемое 60_000 millisecond)
MAGIC = 9876543210  # идентификатор эксперта
DEVIATION = 20  # допустимое отклонение цены в пунктах при совершении сделки
lieder_balance = 0  # default var
lieder_equity = 0  # default var
lieder_positions = []  # default var
lieder_existed_position_tickets = []  # default var
UTC_OFFSET = datetime.now() - datetime.utcnow()
SERVER_DELTA_TIME = timedelta(hours=4)
investors_disconnect_store = [[], []]
old_investors_balance = {}
start_date_utc = datetime.now().replace(microsecond=0)
trading_event = asyncio.Event()  # init async event

EURUSD = USDRUB = EURRUB = -1
send_messages = True  # отправлять сообщения в базу
sleep_lieder_update = 1 # пауза для обновления лидера

host = 'https://my.atimex.io:8000/api/demo_mt5/'

source = {
    # 'lieder': {},
    # 'investors': [{}, {}],
    # 'settings': {}
}
