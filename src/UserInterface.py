from config import FIRST_NAME
from datetime import datetime
import pytz
import time
import tools

class UserInterface():
    def __init__(self, Task):
        self.task = Task

    def main_commands_handler(self):
        command = input(
            f"Добро пожаловать, {FIRST_NAME}!!! \n Для управления программой используются следующие команды: \n"
            f" 'Купить' - для покупки криптовалюты \n 'Продать' - для продажи криптовалюты\n "
            f"'Рассчитать' - для расчёта убытков и прибылей \n")

        if command.lower() == 'купить':
            self.buy_commands_handler()
        elif command.lower() == 'продать':
            self.sell_commands_handler()
        elif command.lower() == 'рассчитать':
            self.calulation_commands_handler()
        else:
            print("Введена неверная команда \n")
            self.main_commands_handler()

    # buy_commands---------------------------------------------------------------------------------------------------------

    def buy_commands_handler(self):
        currency_from = "RUB"
        currency_to = self.choose_currence_to()
        value_from = self.choose_value_from(currency_from)
        value_to = self.task.calculate_value_to(currency_from, currency_to, value_from)
        date_time = datetime.now().strftime("%s")
        self.task.in_change_currency(date_time, self.task.telegram_id, currency_from=currency_from,
                                     currency_to=currency_to, value_from=value_from, value_to=value_to)
        print(f"\n **Вы приобрели {value_to:.6f} {currency_to} на сумму {value_from:.2f} {currency_from}** \n")
        self.main_commands_handler()


    def choose_currence_to(self):
        balance = self.task.get_wallet_balance()
        command = input(f"Ваш баланс {balance['RUB']} рублей. Выберите покупаемую валюту: \n 1.Monero - 'XMR' \n"
                            f"2.Ethereum - 'ETH'\n 3. Tronix - 'TRX' \n"
                            f"4.TON Crystal - 'TON'\n 5.Tether - 'USDT'\n"
                            f"6.Bitcoin - 'BTC' \n")
        if command not in self.task.currencies:
            print("Валюта покупки выбрана неверно \n")
            self.choose_currence_to()
        else:
            return command

    def choose_value_from(self, cur_from):
        balance_cur_to = self.task.get_wallet_balance()[cur_from]
        command = input(f"Введите сумму покупки в {cur_from} \n")
        try:
            value_from = tools.dectimal_converter(value=command, currency=cur_from)
            if value_from <= balance_cur_to:
                return value_from
            else:
                raise ValueError
        except ValueError:
            print("\n **Сумма введена неверно** \n")
            self.choose_value_from(cur_from)


    # sell_commands-----------------------------------------------------------------------------------------------------

    def sell_commands_handler(self):
        currency_to = "RUB"
        currency_from = self.choose_crpt_currency_from()

        value_from = self.choose_crpt_value_from(currency_from)
        value_to = self.task.calculate_value_to(currency_from, currency_to, value_from)  # returns Dectimal

        date_time = datetime.now().strftime("%s")
        self.task.in_change_currency(date_time, self.task.telegram_id, currency_from=currency_from,
                                     currency_to=currency_to, value_from=value_from, value_to=value_to)
        print(f"\n **Вы продали {value_from:.6f} {currency_from} на сумму  {value_to:.2f} {currency_to}** \n")
        self.main_commands_handler()

    def choose_crpt_currency_from(self):
        balance = self.task.get_wallet_balance()
        positive_balances = []
        for key in balance.keys():
            if balance[key] and key != "RUB":
                positive_balances.append(key)

        if positive_balances:
            items = [f'{item}: {balance[item]} \n' for item in positive_balances]
            blns_str = "".join(items)

            command = input(
                f"Ваш баланс криптовалюты: \n {blns_str} \n"
                f"Введите заглавные буква валюты, которую вы хотите продать (к примеру, XMR для Monero) \n")
        else:
            print("\n **На вашем счёте нет криптовалюты** \n")
            self.main_commands_handler()

        if command.upper() in positive_balances:
            return command.upper()

        else:
            print("\n **Валюта покупки выбрана неверно** \n")
            self.main_commands_handler()


    def choose_crpt_value_from(self, cur_from: str):
        balance_cur_to = self.task.get_wallet_balance()[cur_from]
        command = input("Введите сумму криптовалюты, которую вы хотите продать \n")
        try:
            value_from = tools.dectimal_converter(value=command, currency=cur_from)
            if value_from <= balance_cur_to:
                return value_from
            else:
                raise ValueError
        except ValueError:
            print("\n **Сумма введена неверно** \n")
            self.main_commands_handler()

    # calculation_commands------------------------------------------------------------------------------------------
    def calulation_commands_handler(self):
        string_exchanges = self.show_all_ecxhanges_handler()
        command = input(f"\n{string_exchanges if string_exchanges.strip() else 'У вас нет операци покупок/продаж'} \n"
                        f"\n Чтобы узнать общую прибыть, введите 'Прибыль'"
                        f"Для вовзрата в главное меню введите 'Выйти' \n")
        if command.lower() == 'прибыль':
            self.profit_handler()

        elif command.lower() == 'выйти':
            self.main_commands_handler()

    def profit_handler(self) -> None:
        done_operations = self.task.calculate_transactions_profits()
        output_string = ""
        general_profit = 0
        for operation in done_operations:
            timestamp = operation["timestamp"]
            formatted_date_time = datetime.fromtimestamp(int(timestamp), pytz.timezone('Europe/Moscow')).strftime(
                '%Y-%m-%d %H:%M:%S')
            output_string += (f"{formatted_date_time}: продажа {float(operation['value']):.6f} {operation['currency']} принесла"
                              f"{float(operation['profit']):.2f} рублей прибыли \n")
            general_profit +=  operation['profit']

        general_profit_str = f"\n Общая прибыль по всем операциям: {general_profit} \n"
        if output_string == '':
            output_string = '\n **Пока нет завершённых операций. \n'
            general_profit_str = ''
        command = input(f"{output_string} {general_profit_str} \n Для вовзрата в главное меню введите 'Выйти'")

        if command.lower() == 'выйти':
            self.main_commands_handler()

    def prepare_exchanges_data(self, exchanges: list) -> list:
        arr = []
        for exchange in exchanges:
            timestamp = exchange["DateTime"]
            formatted_date_time = datetime.fromtimestamp(int(timestamp), pytz.timezone('Europe/Moscow')).strftime(
                '%Y-%m-%d %H:%M:%S')
            to_currency = exchange["ToCurrency"]
            from_currency = exchange["FromCurrency"]
            from_value = exchange["FromValue"]
            to_value = exchange['ToValue']
            currency_rate_from = self.task.get_current_transaction_info(timestamp).currencyRateFrom
            currency_rate_to = self.task.get_current_transaction_info(timestamp).currencyRateTo

            arr.append({"date_time": formatted_date_time, "to_currency": to_currency, "from_currency": from_currency,
                        "from_value": from_value, "to_value": to_value, "rate_from": currency_rate_from, "rate_to": currency_rate_to})
        return arr

    def show_all_ecxhanges_handler(self):
        exchanges = self.task.exchanges_filter()
        buy_string = ""
        sell_string = ""
        if exchanges["buy_operations"]:
            buy_string += "Операции покупок: \n"
            f_list = self.prepare_exchanges_data(exchanges["buy_operations"])
            for exch in f_list:
                buy_string += (f"{exch['date_time']}: куплено {float(exch['to_value']):.6f} {exch['to_currency']} на сумму "
                               f"{float(exch['from_value']):.2f} рублей по курсу {exch['rate_from']} рублей за {exch['to_currency']}\n")

        if exchanges["sell_operations"]:
            sell_string += "Операции продаж: \n"
            f_list = self.prepare_exchanges_data(exchanges["sell_operations"])
            for exch in f_list:
                sell_string += (
                    f"{exch['date_time']}: продано {float(exch['from_value']):.6f} {exch['from_currency']} на сумму "
                    f"{float(exch['to_value']):.2f} рублей по курсу {exch['rate_to']} рублей за {exch['from_currency']} \n")

        return f"{buy_string} {sell_string}\n"


    # main_loop-----------------------------------------------------------------------------------------------------
    def main_loop(self):

        while True:
            self.main_commands_handler()