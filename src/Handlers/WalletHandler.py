from src.Handlers import UserHandler
from src.DatabaseModel import *

class WalletHandler:
    def __init__(self, session, users: UserHandler):
        self.__session__ = session
        self.__users__ = users

    def __return_to_Currency(self, currency:str):
        if currency == "XMR":
            return Currency.xmr
        elif currency == "ETH":
            return Currency.eth
        elif currency == "TRX":
            return Currency.trx
        elif currency == "TON":
            return Currency.ton
        elif currency == "USDT":
            return Currency.usdt
        elif currency == "RUB":
            return Currency.rub
        elif currency == "BTC":
            return Currency.bth
        pass

    def get_wallet(self, TelegramId: int):
        user = self.__users__.get_by_id(TelegramId)

        wallet = user.wallet
        return wallet

    def change_wallet(self, telegramId: int, **currencies):
        user = self.__users__.get_by_id(telegramId)
        wallet = user.wallet
        for k, v in currencies.items():
            wallet[k] = v
        #self.__session__.add(wallet)
        self.__session__.commit()
        return user.wallet

    def add_to_wallet(self, telegram_id:int , currency:str, value):
        cur = self.__return_to_Currency(currency)
        wallet:Wallet = self.__session__.query(Wallet).where(Wallet.holderId == telegram_id).first()
        wallet[cur] = value + wallet[cur]
        self.__session__.commit()
        return wallet

    def remove_from_wallet(self, telegram_id:int, currency:str, value):
        cur = self.__return_to_Currency(currency)
        wallet:Wallet = self.__session__.query(Wallet).where(Wallet.holderId == telegram_id).first()
        wallet[cur] = wallet[cur] - value
        self.__session__.commit()
        return wallet


