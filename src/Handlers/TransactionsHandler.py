from src.DatabaseModel import *
from src.Handlers.ITransaction import ITransaction

def __return_to_currency__(currency: str):
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


class TransactionHandler:
    def __init__(self, session):
        self.session = session


    def addExChangeOperation(
            self, date_time, actingUser, currency_from, currency_to, value_from, value_to,
            currency_rate_from, currency_rate_to, commission_rate
    ):
        cur_from = __return_to_currency__(currency_from)
        cur_to = __return_to_currency__(currency_to)

        deposit = Deposit(
            dateTime=date_time, userId=actingUser.telegramId,currency=cur_from,
            value=value_from, currencyRate=currency_rate_from, commissionRate=commission_rate,
            approved=False)
        self.session.add(deposit)
        self.session.commit()

        operation = InternalExchange(
            dateTime=date_time, userId=actingUser.telegramId, currencyFrom=cur_from,
            currencyTo=cur_to, valueFrom=value_from, valueTo=value_to,
            currencyRateFrom=currency_rate_from, currencyRateTo=currency_rate_to,
            commissionRate=commission_rate, approved=False)
        self.session.add(operation)
        self.session.commit()

    def get_change_operation(self, telegram_id, date_time):
        op_to_approve_internal_exchange: InternalExchange = self.session.query(InternalExchange).filter(
            InternalExchange.userId == telegram_id, InternalExchange.dateTime == date_time).first()
        return op_to_approve_internal_exchange

    def approveExChangeOperation(self, telegram_id, date_time):
        ops_to_approve_deposit = self.session.query(Deposit).filter(
            Deposit.userId == telegram_id, Deposit.dateTime == date_time).first()
        ops_to_approve_deposit.approved = True

        op_to_approve_internal_exchange: InternalExchange = self.session.query(InternalExchange).filter(
            InternalExchange.userId == telegram_id, InternalExchange.dateTime == date_time).first()
        op_to_approve_internal_exchange.approved = True
        self.session.commit()
        return op_to_approve_internal_exchange

    def cancelExChangeOperation(self, telegram_id, date_time):
        op_to_approve_deposit: Deposit = self.session.query(Deposit).where(
            Deposit.userId == telegram_id, Deposit.dateTime == date_time).first()
        self.session.delete(op_to_approve_deposit)

        op_to_approve_internal_exchange: InternalExchange = self.session.query(InternalExchange).where(
            InternalExchange.userId == telegram_id, InternalExchange.dateTime == date_time).first()
        self.session.delete(op_to_approve_internal_exchange)

        self.session.commit()

    def approveInChangeOperation(self, telegram_id, date_time):
        op_to_approve_internal_exchange: InternalExchange = self.session.query(InternalExchange).where(
            InternalExchange.userId == telegram_id, InternalExchange.dateTime == date_time).first()
        op_to_approve_internal_exchange.approved = True

        self.session.commit()
        return op_to_approve_internal_exchange

    def abortInChangeOperation(self, telegram_id, date_time):
        op_to_approve_internal_exchange: InternalExchange = self.session.query(InternalExchange).where(
            InternalExchange.userId == telegram_id, InternalExchange.dateTime == date_time).first()
        self.session.delete(op_to_approve_internal_exchange)
        self.session.commit()
        return op_to_approve_internal_exchange

    def addInChangeOperation(
            self, date_time, actingUser, currency_from, currency_to, value_from, value_to,
            currency_rate_from, currency_rate_to, commission_rate
    ):
        cur_from = __return_to_currency__(currency_from)
        cur_to = __return_to_currency__(currency_to)

        operation = InternalExchange(
            dateTime=date_time, userId=actingUser.telegramId, currencyFrom=cur_from,
            currencyTo=cur_to, valueFrom=value_from, valueTo=value_to,
            currencyRateFrom=currency_rate_from, currencyRateTo=currency_rate_to,
            commissionRate=commission_rate, approved=False)
        self.session.add(operation)
        self.session.commit()

    def addInOperation(
            self, actingUser, currency, value, currency_rate, commission_rate, date_time
    ):
        cur = __return_to_currency__(currency)
        operation = Deposit(
            dateTime=date_time, userId=actingUser.telegramId, currency=cur,
            value=value, currencyRate=currency_rate, commissionRate=commission_rate, approved=False
        )
        self.session.add(operation)
        self.session.commit()

    def getInOperation(self, telegramId, dateTime):
        op_to_approve = self.session.query(Deposit).filter(Deposit.userId == telegramId,
                                                           Deposit.dateTime == dateTime).first()

        return op_to_approve

    def approveAddInOperation(self, telegramId, dateTime):
        op_to_approve = self.session.query(Deposit).filter(Deposit.userId == telegramId, Deposit.dateTime == dateTime).first()
        op_to_approve.approved = True
        self.session.commit()
        return op_to_approve

    def cancelAddInOperation(self, telegramId, dateTime):
        op_to_delete = self.session.query(Deposit).\
            filter(Deposit.userId == telegramId, Deposit.dateTime == dateTime).first()
        self.session.delete(op_to_delete)
        self.session.commit()
        return op_to_delete

    def addOutOperation(
            self, actingUser, currency, value, currency_rate, commission_rate, date_time
    ):
        cur = __return_to_currency__(currency)
        operation = Withdraw(
            dateTime=date_time, userId=actingUser.telegramId, currency=cur,
            value=value, currencyRate=currency_rate, commissionRate=commission_rate, approved=False
        )
        self.session.add(operation)
        self.session.commit()

    def getOutOperation(self, telegramId, dateTime):
        op_to_approve = self.session.query(Withdraw).filter(Withdraw.userId == telegramId,
                                                            Withdraw.dateTime == dateTime).first()
        return op_to_approve
    def approveAddOutOperation(self, telegramId, dateTime):
        op_to_approve = self.session.query(Withdraw).filter(Withdraw.userId == telegramId, Withdraw.dateTime == dateTime).first()
        op_to_approve.approved = True
        self.session.commit()
        return op_to_approve

    def cancelAddOutOperation(self, telegramId, dateTime):
        op_to_delete = self.session.query(Withdraw).\
            filter(Withdraw.userId == telegramId, Withdraw.dateTime == dateTime).first()
        self.session.delete(op_to_delete)
        self.session.commit()
        return op_to_delete

    def addTransferOperation(self, dateTime, idFrom, idTo, curencyFrom, currencyTo, valueFrom, valueTo,
                             currencyRateFrom, currencyRateTo):

        operation = InternalP2P(
            date_time=dateTime, user_id_1=idFrom, user_id_2=idTo, currency_from_user_1=curencyFrom,
            currency_from_user_2=currencyTo, value_from_user_1=valueFrom, value_from_user_2=valueTo,
            currency_rate_from_user_1=currencyRateFrom, currency_rate_from_user_2=currencyRateTo, approved=False
        )

        self.session.add(operation)
        self.session.commit()

    def approveTransferOperation(self, telegramIdFrom, telegramIdTo, dateTime):
        op_to_approve = self.session.query(InternalP2P). \
            filter(InternalP2P.userId1 == telegramIdFrom,
                   InternalP2P.userId2 == telegramIdTo,
                   InternalP2P.dateTime == dateTime)\
            .first()

        op_to_approve.approved = True
        self.session.commit()
        return op_to_approve

    def cancelTransferOperation(self, telegramIdFrom, telegramIdTo, dateTime):
        op_to_delete = self.session.query(InternalP2P).\
            filter(InternalP2P.userId1 == telegramIdFrom,
                   InternalP2P.userId2 == telegramIdTo,
                   InternalP2P.dateTime == dateTime)\
            .first()

        self.session.delete(op_to_delete)
        self.session.commit()
        return op_to_delete

    def check_is_one_transaction_exists(self, telegramId):
        user = self.session.query(User).filter(User.telegramId == telegramId).first()
        if user.canInvite:
            return True
        else:
            deposit_op = self.session.query(Deposit).filter(Deposit.userId == telegramId, Deposit.approved).first()
            if deposit_op is not None:
                user.canInvite = True
                self.session.commit()
                return True
            else:
                return False

    def add_profit(self, transactionId, transactionType, telegramId, currency, profit, margin):
        profit_record = Profits(transactionId, transactionType, telegramId, currency, profit, margin)
        self.session.add(profit_record)
        self.session.commit()

    # def get_profits(self, telegram_id):
    #     profits = self.session.query(Profits).filter(Profits.telegramId == telegram_id).all()
    #
    #     return profits

    def getExchanges(self, telegramId) -> list[dict[str]]:
        exchanges: list[ITransaction] = self.session.query(InternalExchange)\
            .filter(InternalExchange.userId == telegramId and InternalExchange.approved).all()
        exchanges += self.session.query(InternalP2P)\
            .filter((InternalP2P.userId1 == telegramId or InternalP2P.userId2 == telegramId)
                    and InternalP2P.approved).all()
        return list(map(lambda exc: exc.serialize_data(), exchanges))