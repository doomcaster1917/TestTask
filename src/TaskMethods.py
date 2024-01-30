from config import TELEGRAM_ID, FIRST_NAME, LAST_NAME, USER_TG_NAME
from DatabaseModel import TransactionType
from decimal import *
import tools
import requests


class Task():
    #Можно было бы унаследоваться от хендлеров, но их инициализацию легче производить в main,
    #передавая из сюда в качестве аргументов
    def __init__(self, TransactionHandler, UserHandler, WalletHandler):
        self.currencies = ["XMR", "ETH", "TRX", "TON", "USDT", "BTC", "RUB"]
        self.telegram_id = TELEGRAM_ID #You can set these values in .env file
        self.first_name = FIRST_NAME
        self.last_name = LAST_NAME
        self.user_name = USER_TG_NAME
        self.transactions_handler = TransactionHandler
        self.user_handler = UserHandler
        self.wallet_handler = WalletHandler

    # tools_methods------------------------------------------------------------------------------------------------------------------------------
    def get_currency_price(self, currency_from: str, currency_to: str):
        URL = f'https://min-api.cryptocompare.com/data/price?fsym={currency_from}&tsyms={currency_to}'
        response = requests.get(URL)
        if currency_to == "RUB":
            dectimal_price = tools.revers_dectimal_converter(response.json()[currency_to]) #см. комментарии к методу
        else:
            dectimal_price = tools.dectimal_converter(response.json()[currency_to], currency_from)
        return dectimal_price

    def get_wallet_balance(self, telegram_id=TELEGRAM_ID):
        wallet = self.wallet_handler.get_wallet(telegram_id)
        balance = { "XMR": wallet.xmrBalance if wallet.xmrBalance else None,
                    "ETH": wallet.ethBalance if wallet.ethBalance else None,
                    "TRX": wallet.trxBalance if wallet.trxBalance else None,
                    "TON": wallet.tonBalance if wallet.tonBalance else None,
                    "BTC": wallet.btcBalance if wallet.btcBalance else None,
                    "USDT": wallet.usdtBalance if wallet.usdtBalance else None,
                    "RUB": wallet.rubBalance if wallet.rubBalance else None}
        return balance

    def get_current_transaction_info(self, date_time, telegram_id=TELEGRAM_ID):
        return self.transactions_handler.get_change_operation(telegram_id, date_time)


    # DB_init_methods------------------------------------------------------------------------------------------------------------------------------
    def add_user(self):
        self.user_handler.add_user(telegram_id=self.telegram_id, chat_id=self.telegram_id, first_name=self.first_name, last_name=self.last_name, canInvite=True,
                             updateLinksTime=15, is_premium=False, user_name=self.user_name)


    def add_start_currency_to_wallet(self):
        value = 1000000
        currency = "RUB"
        self.wallet_handler.add_to_wallet(self.telegram_id, currency, value)

    # DB_methods----------------------------------------------------------------------------------------------------------------------------------
    def in_change_currency(self, date_time:str, telegram_id: int, currency_from: str, currency_to: str, value_from: Decimal, value_to: Decimal):
        actingUser = self.user_handler.get_by_id(telegram_id)
        cur_rate_from = self.get_currency_price(currency_to, currency_from)
        cur_rate_to = self.get_currency_price(currency_from, currency_to)
        comission_rate = 0

        #1 Добавление продаваемой валюты(по заданию - RUB) в депозит
        self.transactions_handler.addInOperation(actingUser, currency_from, value_from, cur_rate_from, comission_rate, date_time)
        self.transactions_handler.approveAddInOperation(telegram_id, date_time)

        #2 Удаление продаваемой валюты(по заданию -  RUB) из кошелька
        self.wallet_handler.remove_from_wallet(telegram_id, currency_from, value_from)

        #3 Добавление обменной операции в таблицу внутренних обменных операций
        self.transactions_handler.addInChangeOperation(date_time=date_time, actingUser=actingUser, currency_from=currency_from, currency_to=currency_to,
                                                value_from=value_from, value_to=value_to, currency_rate_from=cur_rate_from,
                                                currency_rate_to=cur_rate_to, commission_rate=comission_rate)
        self.transactions_handler.approveInChangeOperation(telegram_id=TELEGRAM_ID, date_time=date_time)

        #4 Добавление купленной валюты(крипта) в кошелёк
        self.wallet_handler.add_to_wallet(telegram_id, currency_to, value_to)


        #5 Удаление продаваемой валюты(по заданию -  RUB) из депозита
        self.transactions_handler.addOutOperation(actingUser, currency_from, cur_rate_from, value_from, comission_rate, date_time)

    # calculate_methods---------------------------------------------------------------------------------------------------------------------------
    def exchanges_filter(self) -> dict:
        exchanges = self.transactions_handler.getExchanges(self.telegram_id)
        bought_exchanges = []
        sold_exchanges = []
        if exchanges:
            for exchange in exchanges:
                if exchange['FromCurrency'] == "RUB":
                    bought_exchanges.append(exchange)
                else:
                    sold_exchanges.append(exchange)

        return {"buy_operations": bought_exchanges, "sell_operations": sold_exchanges}

    def calculate_transactions_profits(self):
        # Завершённые операции <Человек купил крипту и через n времени вернул всю сумму или часть от суммы в рубли>
        exchanges = self.exchanges_filter()
        buy_exchanges = exchanges["buy_operations"]
        sell_operations = exchanges["sell_operations"]
        done_operations = []
        for sell in sell_operations:
            for buy in buy_exchanges:
                if sell['ToCurrency'] == buy['FromCurrency'] and sell['DateTime'] > buy['DateTime']:
                    current_sell_info = self.get_current_transaction_info(sell['DateTime'])
                    current_buy_info = self.get_current_transaction_info(buy['DateTime'])
                    timestamp = sell['DateTime']
                    currency = sell['FromCurrency']
                    profit = float(sell["FromValue"]) * float(current_sell_info.currencyRateTo - current_buy_info.currencyRateFrom) # в рублях
                    done_operations.append({"timestamp": timestamp,"currency": currency, "profit": profit, "value": sell["FromValue"]})

                    #Не входит в задание, но оставлю на всякий случай.
                    #Возможно, вообще следовало бы в методе in_change_currency добавить этот код и
                    #сохранять профиты при каждой операции перевода крипты в RUB
                    """transaction_id = sell['transactionId']
                    transaction_type = TransactionType.exchange
                    telegram_id = sell['userId']
                    margin = sell["valueTo"] * (current_sell_info.currencyRateFrom - current_buy_info.currencyRateTo)  # в криптовалюте
                    self.transactions_handler.add_profit(transaction_id, transaction_type, telegram_id, currency, profit, margin)"""

        return done_operations

    def calculate_general_profit(self, transactions: list[dict]):
        ...
    def calculate_value_to(self, currency_from: str, currency_to: str, value_from: Decimal):
        price_to = self.get_currency_price(currency_to, currency_from)
        value_to = value_from/price_to
        return value_to



