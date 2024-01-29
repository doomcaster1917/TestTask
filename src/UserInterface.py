from config import FIRST_NAME
from datetime import datetime
import os

class UserInterface():
    def __init__(self, Task):
        self.task = Task

    def main_commands_handler(self):
        command = input(
            f"Добро пожаловать, {FIRST_NAME}!!! \n Для управления программой используются следующие команды: \n"
            f" 'Купить' - для покупки криптовалюты \n 'Продать' - для продажи криптовалюты\n "
            f"'Рассчитать' - для расчёта убытков и прибылей")

        if command.lower() == 'купить':
            self.buy_commands_handler()
        elif command.lower() == 'продать':
            self.sell_commands_handler()
        elif command.lower() == 'рассчитать':
            ...
        else:
            print("Введена неверная команда \n")
            self.main_commands_handler()

    # buy_commands---------------------------------------------------------------------------------------------------------

    def buy_commands_handler(self):
        currence_from = "RUB"
        currency_to = self.choose_currence_to()
        value_from = self.choose_value_from(currence_from)

        value_to = self.task.calculate_value_to(currence_from, currency_to, value_from) # returns Dectimal

        date_time = datetime.now().strftime("%s")
        self.task.in_change_currency(date_time, self.task.telegram_id, currency_from=currence_from,
                                     currency_to=currency_to, value_from=value_from, value_to=value_to)
        print(f"Вы приобрели {value_to} {currency_to} на сумму {value_from} {currence_from}")
        self.main_commands_handler()


    def choose_currence_to(self):
        balance = self.task.get_wallet_balance()
        command = input(f"Ваш баланс {balance['RUB']} рублей. Выберите покупаемую валюту: \n 1.Monero - 'XMR' \n"
                            f"2.Ethereum - 'ETH'\n 3. Tronix - 'TRX' \n"
                            f"4.TON Crystal - 'TON'\n 5.Tether - 'USDT'\n"
                            f"6.Bitcoin - 'BTC'")
        if command not in self.task.currencies:
            print("Валюта покупки выбрана неверно \n")
            self.choose_currence_to()
        else:
            return command

    def choose_value_from(self, cur_from):
        balance_cur_to = self.task.get_wallet_balance()[cur_from]
        command = input(f"Введите сумму покупки в {cur_from}")
        if not command.isdigit() and int(command) > balance_cur_to:
            print("Сумма покупки введена неверно \n")
            self.choose_value_from(cur_from)
        else:
            return int(command)


    # sell_commands-----------------------------------------------------------------------------------------------------

    def sell_commands_handler(self):
        currency_to = "RUB"
        currency_from = self.choose_crpt_currency_from()

        value_from = self.choose_crpt_value_from(currency_from)
        value_to = self.task.calculate_value_to(currency_from, currency_to, value_from)  # returns Dectimal

        date_time = datetime.now()
        self.task.in_change_currency(date_time, self.task.telegram_id, currency_from=currency_from,
                                     currency_to=currency_to, value_from=value_from, value_to=value_to)
        print(f"Вы продали {value_to} {currency_to} на сумму {value_from} {currency_from}")
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
                f"Ваш баланс криптовалюты: \n {blns_str}"
                f"Введите заглавные буква валюты, которую вы хотите продать (к примеру, XMR для Monero)")
        else:
            print("\n **На вашем счёте нет криптовалюты** \n")
            self.main_commands_handler()

        if command.upper() in positive_balances:
            return command.upper()

        else:
            print("\n **Валюта покупки выбрана неверно** \n")
            self.choose_crpt_currency_from()


    def choose_crpt_value_from(self, currency: str):
        balance_cur_to = self.task.get_wallet_balance()[currency]
        command = input("Введите сумму криптовалюты, которую вы хотите продать")
        if command.isdigit() and int(command) <= balance_cur_to:
            return int(command)

    def main_loop(self):

        while True:
            self.main_commands_handler()