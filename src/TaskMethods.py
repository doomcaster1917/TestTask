from config import TELEGRAM_ID, FIRST_NAME, LAST_NAME, USER_TG_NAME
from Exceptions import *
from decimal import *
import requests


class Task():
    #Можно было бы унаследоваться от хендлеров, но их инициализацию легче производить в main,
    #передавая из сюда в качестве аргументов
    def __init__(self, TransactionHandler, UserHandler, WalletHandler):
        self.currencies = ["XMR", "ETH", "TRX", "TON", "USDT", "BTC", "RUB", "USD"]
        self.telegram_id = TELEGRAM_ID #You can set these values in .env file
        self.first_name = FIRST_NAME
        self.last_name = LAST_NAME
        self.user_name = USER_TG_NAME
        self.transactions_handler = TransactionHandler
        self.user_handler = UserHandler
        self.wallet_handler = WalletHandler

    # tools_methods------------------------------------------------------------------------------------------------------------------------------
    def get_currency_price(self, currency_from: str, currency_to: str):
        print(currency_to, currency_from)
        if currency_from not in self.currencies or currency_to not in self.currencies:
            raise NotRightCurName
        elif currency_to == currency_from:
            raise MatchingDuplicateCurs
        else:
            URL = f'https://min-api.cryptocompare.com/data/price?fsym={currency_from}&tsyms={currency_to}'
            response = requests.get(URL)
            return response.json()[currency_to]

    def get_wallet_balance(self, telegram_id=TELEGRAM_ID):
        wallet = self.wallet_handler.get_wallet(telegram_id)
        balance = { "XMR": wallet.xmrBalance if wallet.xmrBalance else None,
                    "ETH": wallet.ethBalance if wallet.trxBalance else None,
                    "TON": wallet.tonBalance if wallet.usdtBalance else None,
                    "BTC": wallet.btcBalance if wallet.btcBalance else None,
                    "USDT": wallet.usdtBalance if wallet.usdtBalance else None,
                    "RUB": wallet.rubBalance if wallet.rubBalance else None}
        return balance

    # DB_init_methods------------------------------------------------------------------------------------------------------------------------------
    def add_user(self):
        self.user_handler.add_user(telegram_id=self.telegram_id, chat_id=self.telegram_id, first_name=self.first_name, last_name=self.last_name, canInvite=True,
                             updateLinksTime=15, is_premium=False, user_name=self.user_name)


    def add_start_currency_to_wallet(self):
        value = 1000000
        currency = "RUB"
        self.wallet_handler.add_to_wallet(self.telegram_id, currency, value)

    # DB_methods----------------------------------------------------------------------------------------------------------------------------------
    def in_change_currency(self, date_time:str, telegram_id: int, currency_from: str, currency_to: str, value_from: str, value_to: Decimal):
        actingUser = self.user_handler.get_by_id(telegram_id)
        cur_rate_from = self.get_currency_price(currency_from, currency_to)
        cur_rate_to = self.get_currency_price(currency_to, currency_from)
        comission_rate = 0

        #1 Добавление продаваемой валюты(по заданию - USD или RUB) в депозит
        self.transactions_handler.addInOperation(actingUser, currency_from, value_from, cur_rate_from, comission_rate, date_time)
        self.transactions_handler.approveAddInOperation(telegram_id, date_time)

        #2 Удаление продаваемой валюты(по заданию - USD или RUB) из кошелька
        self.wallet_handler.remove_from_wallet(telegram_id, currency_from, value_from)

        #3 Добавление обменной операции в таблицу внутренних обменных операций
        self.transactions_handler.addInChangeOperation(date_time=date_time, actingUser=actingUser, currency_from=currency_from, currency_to=currency_to,
                                                value_from=value_from, value_to=value_to, currency_rate_from=cur_rate_from,
                                                currency_rate_to=cur_rate_to, commission_rate=comission_rate)
        self.transactions_handler.approveInChangeOperation(telegram_id=TELEGRAM_ID, date_time=date_time)

        #4 Добавление купленной валюты(крипта) в кошелёк
        self.wallet_handler.add_to_wallet(telegram_id, currency_to, value_to)


        #5 Удаление продаваемой валюты(по заданию - USD или RUB) из депозита
        self.transactions_handler.addOutOperation(actingUser, currency_from, cur_rate_from, value_from, comission_rate, date_time)

    # calculate_methods---------------------------------------------------------------------------------------------------------------------------
    def calculate_transactions_profits(self, telegram_id: int, transactions: list[dict]):
        for transaction in transactions:
            ...
        ...

    def calculate_general_profit(self, transactions: list[dict]):
        for transaction in transactions:
            ...
        ...

    def calculate_value_to(self, currency_from: str, currency_to: str, value_from: float):
        price_to = self.get_currency_price(currency_to, currency_from) #Цена крипты в RUB/USD
        value_to = value_from/price_to
        dectimal_to = Decimal(value_to).quantize(Decimal('.00'), rounding=ROUND_DOWN)
        return dectimal_to



