""" Не совсем понял, предназначение таблицы Profits, поскольку она не указана в отношениях других таблиц,
а в TransactionsHandler есть метод add_profit, но даже нет метода get_profits.

Я сначала предполагал, что задание неявно подразумевает использование этой таблицы и написание методов для работый с ней.
Но позже отказался от её использования, поскольку в таблице нет нужных мне полей - date_time, valueFrom, valueTo

А гонять лишний раз информацию по базе данных - не лучший вариант с точки зрения скорости работы сервиса"""


def get_profits(self, telegram_id):
    profits = self.session.query(Profits).filter(Profits.telegramId == telegram_id).all()

    return profits
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