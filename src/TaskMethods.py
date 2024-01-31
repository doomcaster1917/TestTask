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
        op = self.transactions_handler.approveInChangeOperation(telegram_id=TELEGRAM_ID, date_time=date_time)

        #4 Добавление купленной валюты(крипта) в кошелёк
        self.wallet_handler.add_to_wallet(telegram_id, currency_to, value_to)


        #5 Удаление продаваемой валюты(по заданию - RUB) из депозита
        self.transactions_handler.addOutOperation(actingUser, currency_from, cur_rate_from, value_from, comission_rate, date_time)


        #6 Если операция - продажа (обмен криты на рубли), то сохранить profit(в рублях) и margin (разница в курсе крипты)
        if currency_to == "RUB":
            self.save_profit(op)


    def save_profit(self, sell_transaction):
        # Если есть операция продажи крипты, надо найти последнюю операцию покупки этой крипты и взять из неё курс

        currency = sell_transaction.currencyFrom  # Проданная крипта = крипта, которую когда-то купили
        exchanges = self.transactions_handler.getExchanges(self.telegram_id)
        buy_operations = []
        for exch in exchanges:
            if exch['FromCurrency'] == currency:
                buy_operations.append(exch)

        buy_date_times = [op['DateTime'] for op in buy_operations]
        last_buy_op_index = buy_date_times.index(str(max(buy_date_times)))

        current_sell_info = self.get_current_transaction_info(sell_transaction.dateTime)
        current_buy_info = self.get_current_transaction_info(buy_operations[last_buy_op_index]['DateTime'])

        transaction_id = sell_transaction.transactionId
        transaction_type = buy_operations[last_buy_op_index]['Type']
        telegram_id = sell_transaction.userId

        profit = (float(sell_transaction.valueFrom) *
                  float(current_sell_info.currencyRateTo - current_buy_info.currencyRateFrom))  # в рублях

        margin = current_sell_info.currencyRateFrom - current_buy_info.currencyRateTo  # разница курсов крипты
        self.transactions_handler.add_profit(transaction_id, transaction_type, telegram_id, currency, profit, margin)


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
        buy_operations = exchanges["buy_operations"]
        sell_operations = exchanges["sell_operations"]
        done_operations = []
        print(f"{len(sell_operations)} продаж {len(buy_operations)} покупок")
        for sell in sell_operations:

            currency = sell['FromCurrency'] # Проданная крипта = крипта, которую когда-то купили
            value = sell["FromValue"]

            # Поиск покупок проданной крипты
            currency_buy_operations = []
            for op in buy_operations:
                if op['ToCurrency'] == currency:
                    currency_buy_operations.append(op)

            # Поиск индекса последней (с наиб. timestamp) покупки этой крипты
            buy_date_times = [op['DateTime'] for op in currency_buy_operations]
            last_buy_op_index = buy_date_times.index(str(max(buy_date_times)))

            buy_info = self.get_current_transaction_info(currency_buy_operations[last_buy_op_index]['DateTime'])
            sell_info = self.get_current_transaction_info(sell['DateTime'])

            timestamp = sell['DateTime']
            currency = sell['FromCurrency']
            print(value, sell_info.currencyRateTo, buy_info.currencyRateFrom)
            profit = float(value) * float(sell_info.currencyRateTo - buy_info.currencyRateFrom)  # в рублях
            done_operations.append(
                {"timestamp": timestamp, "currency": currency, "profit": profit, "value": sell["FromValue"]})

        return done_operations

    def calculate_value_to(self, currency_from: str, currency_to: str, value_from: Decimal):
        price_to = self.get_currency_price(currency_to, currency_from)
        value_to = value_from/price_to
        return value_to



