from decimal import Decimal
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import relationship
from src.Handlers.ITransaction import ITransaction
from enum import Enum


Base = declarative_base()


class Currency(Enum):
    bth = 0
    eth = 1
    trx = 2
    ton = 3
    usdt = 4
    rub = 5
    xmr = 6

    def __str__(self):
        if self == Currency.xmr: # криптовалюта Monero
            return "XMR"
        elif self == Currency.eth: # криптовалюта Ethereum
            return "ETH"
        elif self == Currency.trx: # криптовалюта Tronix
            return "TRX"
        elif self == Currency.ton: # криптовалюта TON Crystal
            return "TON"
        elif self == Currency.usdt: # криптовалюта Tether
            return "USDT"
        elif self == Currency.rub: # валюта Рубли
            return "RUB"
        elif self == Currency.bth: # криптовалюта Биткойн
            return "BTC"
        pass

# ===========================================================================================================================================
#           class TransactionType - ...
# ===========================================================================================================================================
class TransactionType(Enum):
    exchange = 1
    deposit = 2
    withdraw = 3
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        if self == TransactionType.exchange:
            return "iex"
        elif self == TransactionType.deposit:
            return "d"
        elif self == TransactionType.withdraw:
            return "w"
# ===========================================================================================================================================
#           class User - ...
# ===========================================================================================================================================
class User(Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    telegramId = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, nullable=True)
    isPremium = Column(Boolean)
    languageCode = Column(String)
    referralId = Column(BigInteger,
                        ForeignKey('user.telegramId', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    firstName = Column(String)
    lastName = Column(String)
    username = Column(String)
    canInvite = Column(Boolean)
    updateLinksTime = Column(String)
    refLinks = Column(Integer)
    profitPercent = Column(DECIMAL(8, 2))
    banned = Column(Boolean)
    inviter = relationship('User', remote_side=[telegramId], backref='invitees')
    wallet = relationship('Wallet', backref='user', uselist=False)
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, telegramId, first_name, last_name, username, canInvite, updateLinksTime, chat_id, inviter_id,
                 language_code, is_premium, ref_links, banned=False):
        self.telegramId = telegramId
        self.firstName = first_name
        self.lastName = last_name
        self.username = username
        self.canInvite = canInvite
        self.updateLinksTime = updateLinksTime
        self.chat_id = chat_id  # айди персонального чата
        self.referralId = inviter_id  # айди того, кто пригласил пользователя
        self.languageCode = language_code
        self.isPremium = is_premium
        self.refLinks = ref_links  # колличество реферальных ссылок
        self.profitPercent = Decimal('10.00')
        self.banned = banned
        self.wallet = Wallet()
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        return f'{self.telegramId} | {self.chat_id} | {self.firstName} | {self.lastName} | {self.username} |\n' \
            + f'{self.canInvite} | {self.referralId} | {self.isPremium} | {self.languageCode} |\n' + f' {self.wallet}'

# ===========================================================================================================================================
#           class Wallet - ...
# ===========================================================================================================================================
class Wallet(Base):
    __tablename__ = 'wallet'
    __table_args__ = {'extend_existing': True}

    walletId = Column(BigInteger, primary_key=True)
    holderId = Column(BigInteger, ForeignKey('user.telegramId', onupdate="CASCADE", ondelete="CASCADE"))
    btcBalance = Column(DECIMAL(32, 8))
    ethBalance = Column(DECIMAL(32, 18))
    trxBalance = Column(DECIMAL(32, 16))
    tonBalance = Column(DECIMAL(32, 9))
    xmrBalance = Column(DECIMAL(32, 12))
    usdtBalance = Column(DECIMAL(32, 2))
    rubBalance = Column(DECIMAL(32, 2))
    activated = Column(Boolean)
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, key):
        if key == Currency.xmr:
            return self.xmrBalance
        elif key == Currency.eth:
            return self.ethBalance
        elif key == Currency.trx:
            return self.trxBalance
        elif key == Currency.ton:
            return self.tonBalance
        elif key == Currency.usdt:
            return self.usdtBalance
        elif key == Currency.rub:
            return self.rubBalance
        elif key == Currency.bth:
            return self.btcBalance
        else:
            raise ValueError('Currency is not supported!')
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __setitem__(self, key, value):
        if key == Currency.xmr:
            self.xmrBalance = value
        elif key == Currency.eth:
            self.ethBalance = value
        elif key == Currency.trx:
            self.trxBalance = value
        elif key == Currency.ton:
            self.tonBalance = value
        elif key == Currency.usdt:
            self.usdtBalance = value
        elif key == Currency.rub:
            self.rubBalance = value
        elif key == Currency.bth:
            self.btcBalance = value
        else:
            raise ValueError('Currency is not supported!')
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        self.btcBalance = 0
        self.ethBalance = 0
        self.usdtBalance = 0
        self.rubBalance = 0
        self.trxBalance = 0
        self.tonBalance = 0
        self.xmrBalance = 0
        self.activated = True
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        return f'BTC: {self.btcBalance:.6f} ETH: {self.ethBalance:.5f} USDT: {self.usdtBalance:.2f}\
         TRX: {self.trxBalance:.3f} 'f'TON: {self.tonBalance:.3f} XMR: {self.xmrBalance:.4f} RUB: {self.rubBalance:.2f}'
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return self.__repr__()

# ===========================================================================================================================================
#           class InternalP2P - ...
# ===========================================================================================================================================
class InternalP2P(Base, ITransaction):
    __tablename__ = 'internal_p2p'
    __table_args__ = {'extend_existing': True}

    transactionId = Column(BigInteger, primary_key=True)
    dateTime = Column(String)
    userId1 = Column(BigInteger, ForeignKey('user.telegramId', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    userId2 = Column(BigInteger, ForeignKey('user.telegramId', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    currencyFromUser1 = Column(String)
    currencyFromUser2 = Column(String)
    valueFromUser1 = Column(DECIMAL(32, 16))
    valueFromUser2 = Column(DECIMAL(32, 16))
    currencyRateFromUser1 = Column(DECIMAL(32, 2))  # пересчет отностилеьно рублях
    currencyRateFromUser2 = Column(DECIMAL(32, 2))
    approved = Column(Boolean)
    sender = relationship('User', foreign_keys=[userId1], backref='sent_operations')
    receiver = relationship('User', foreign_keys=[userId2], backref='received_operations')
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 date_time: str,
                 user_id_1: int,
                 user_id_2: int,
                 currency_from_user_1: Currency,
                 currency_from_user_2: Currency,
                 value_from_user_1: Decimal(),
                 value_from_user_2: Decimal(),
                 currency_rate_from_user_1: Decimal(),
                 currency_rate_from_user_2: Decimal(),
                 approved: bool
                 ):
        self.dateTime = date_time
        self.userId1 = user_id_1
        self.userId2 = user_id_2
        self.currencyFromUser1 = currency_from_user_1.__str__()
        self.currencyFromUser2 = currency_from_user_2.__str__()
        self.valueFromUser1 = value_from_user_1
        self.valueFromUser2 = value_from_user_2
        self.currencyRateFromUser1 = currency_rate_from_user_1
        self.currencyRateFromUser2 = currency_rate_from_user_2
        self.approved = approved
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def serialize_data(self) -> dict[str]:
        return dict(
            Type="Internal P2P Operation",
            DateTime=str(self.dateTime),
            From=str(self.userId1),
            To=str(self.userId2),
            FromCurrency=str(self.currencyFromUser1),
            ToCurrency=str(self.currencyFromUser2),
            FromValue=str(self.valueFromUser1),
            ToValue=str(self.valueFromUser2)
        )
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        return f'{self.type}' \
            + f' P2P - |user1|  {self.sender.telegramId}: {self.valueFromUser1} {self.currencyFromUser1} \
               (rate: {self.currencyRateFromUser1})' + f' \n|user2| {self.receiver.telegramId}: {self.valueFromUser2}\
                {self.currencyFromUser2} (rate: {self.currencyRateFromUser2})' + f'| Approved {self.Approved}'
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return self.__repr__()

# ===========================================================================================================================================
#           class InternalExchange - ...
# ===========================================================================================================================================
class InternalExchange(Base, ITransaction):
    __tablename__ = 'internal_exchange'
    __table_args__ = {'extend_existing': True}

    transactionId = Column(BigInteger, primary_key=True)
    dateTime = Column(String)
    userId = Column(BigInteger, ForeignKey('user.telegramId', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    currencyFrom = Column(String)
    currencyTo = Column(String)
    valueFrom = Column(DECIMAL(32, 16))
    valueTo = Column(DECIMAL(32, 16))
    currencyRateFrom = Column(DECIMAL(32, 2))
    currencyRateTo = Column(DECIMAL(32, 2))
    commissionRate = Column(DECIMAL(8, 2))
    approved = Column(Boolean)
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 dateTime: str,
                 userId: int,
                 currencyFrom: Currency,
                 currencyTo: Currency,
                 valueFrom: Decimal,
                 valueTo: Decimal,
                 currencyRateFrom: Decimal,
                 currencyRateTo: Decimal,
                 commissionRate: Decimal,
                 approved: bool
                 ):
        self.dateTime = dateTime
        self.userId = userId
        self.currencyFrom = currencyFrom.__str__()
        self.currencyTo = currencyTo.__str__()
        self.valueFrom = valueFrom
        self.valueTo = valueTo
        self.currencyRateFrom = currencyRateFrom
        self.currencyRateTo = currencyRateTo
        self.commissionRate = commissionRate
        self.approved = approved
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def serialize_data(self) -> dict[str]:
        return dict(
            Type="Internal Exchange",
            DateTime=str(self.dateTime),
            From=str(self.userId),
            To=str(self.userId),
            FromCurrency=str(self.currencyFrom),
            ToCurrency=str(self.currencyTo),
            FromValue=str(self.valueFrom),
            ToValue=str(self.valueTo)
        )
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        pass
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        pass

# ===========================================================================================================================================
#           class Deposit - ...
# ===========================================================================================================================================
class Deposit(Base, ITransaction):
    __tablename__ = 'deposit'
    __table_args__ = {'extend_existing': True}

    transactionId = Column(BigInteger, primary_key=True)
    dateTime = Column(String)
    userId = Column(BigInteger, ForeignKey('user.telegramId', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    currency = Column(String)
    value = Column(DECIMAL(32, 16))
    currencyRate = Column(DECIMAL(32, 2))
    commissionRate = Column(DECIMAL(8, 2))
    approved = Column(Boolean)
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 dateTime: str,
                 userId: int,
                 currency: Currency,
                 value: Decimal,
                 currencyRate: Decimal,
                 commissionRate: Decimal,
                 approved: bool
                 ):
        self.dateTime = dateTime
        self.userId = userId
        self.currency = currency.__str__()
        self.value = value
        self.currencyRate = currencyRate
        self.commissionRate = commissionRate
        self.approved = approved
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def serialize_data(self) -> dict[str]:
        return dict(
            Type="Deposit",
            DateTime=str(self.dateTime),
            From=str(self.userId),
            To=str(self.userId),
            FromCurrency=str(None),
            ToCurrency=str(self.currency),
            FromValue=str(None),
            ToValue=str(self.value)
        )
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        pass
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        pass

# ===========================================================================================================================================
#           class Withdraw - ...
# ===========================================================================================================================================
class Withdraw(Base, ITransaction):
    __tablename__ = 'withdraw'
    __table_args__ = {'extend_existing': True}

    transactionId = Column(BigInteger, primary_key=True)
    dateTime = Column(String)
    userId = Column(BigInteger, ForeignKey('user.telegramId', onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    currency = Column(String)
    value = Column(DECIMAL(32, 16))
    currencyRate = Column(DECIMAL(32, 2))
    commissionRate = Column(DECIMAL(8, 2))
    approved = Column(Boolean)
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 dateTime: str,
                 userId: int,
                 currency: Currency,
                 value: Decimal,
                 currencyRate: Decimal,
                 commissionRate: Decimal,
                 approved: bool
                 ):
        self.dateTime = dateTime
        self.userId = userId
        self.currency = currency.__str__()
        self.value = value
        self.currencyRate = currencyRate
        self.commissionRate = commissionRate
        self.approved = approved
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def serialize_data(self) -> dict[str]:
        return dict(
            Type="Withdraw",
            DateTime=str(self.dateTime),
            From=str(self.userId),
            To=str(self.userId),
            FromCurrency=str(self.currency),
            ToCurrency=str(None),
            FromValue=str(self.value),
            ToValue=str(None)
        )
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        pass
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        pass

# ===========================================================================================================================================
#           class GroupLink - ...
# ===========================================================================================================================================
class GroupLink(Base):
    __tablename__ = 'group_link'
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger)
    activated = Column(Boolean)
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.activated = False

# ===========================================================================================================================================
#           class Profits - ...
# ===========================================================================================================================================
class Profits(Base):
    __tablename__ = 'profits'
    __table_args__ = {'extend_existing': True}
    transactionId = Column(BigInteger, primary_key=True)
    transactionType = Column(String, primary_key=True)
    telegramId = Column(BigInteger)
    currency = Column(String)
    profit = Column(DECIMAL(32, 8))
    margin = Column(DECIMAL(32, 8))
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, transactionId, transactionType, telegramId, currency, profit, margin):
        self.transactionId = transactionId
        self.transactionType = transactionType
        self.telegramId = telegramId
        self.currency = currency
        self.profit = profit
        self.margin = margin
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        pass
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        pass

# ===========================================================================================================================================
#           class Invited - ...
# ===========================================================================================================================================
class Invited(Base):
    __tablename__ = 'invited'
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    referral = Column(BigInteger, ForeignKey('user.telegramId'), nullable=False)
    invitees = Column(BigInteger, ForeignKey('user.telegramId'), nullable=False)

# ===========================================================================================================================================
#           class CommissionRates - ...
# ===========================================================================================================================================
class CommissionRates(Base):
    __tablename__ = 'rates'
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True)
    currency_from = Column(String)
    currency_to = Column(String)
    commission_pct = Column(DECIMAL(8, 2))
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, currency_from, currency_to, commission_pct=0):
        self.currency_from = currency_from
        self.currency_to = currency_to
        self.commission_pct = commission_pct

# ===========================================================================================================================================
#           class WithdrawComissions - ...
# ===========================================================================================================================================
class WithdrawComissions(Base):
    __tablename__ = 'withdraw_comissions'
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True)
    currency = Column(String)
    commission_pct = Column(DECIMAL(8, 2))
    # -------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, currency, commission_pct=0):
        self.currency = currency
        self.commission_pct = commission_pct

# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------


