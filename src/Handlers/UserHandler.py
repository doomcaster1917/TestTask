from src.Handlers.RetCodes import RetCode
from src.DatabaseModel import *


class UserHandler:
    def __init__(self, session):
        self.__session__ = session

    def get_by_id(self, telegram_id: int) -> User:
        return self.__session__.query(User).where(User.telegramId == telegram_id).first()

    def add_user(self, telegram_id: int, chat_id: int,  first_name: str, last_name: str, user_name,
                 canInvite: bool, updateLinksTime: String, is_premium: bool, ref_links: int = 2,
                 language_code: str = 'ENG', inviter_telegram_id: int = None) -> RetCode:

        if self.get_by_id(telegram_id):
            return RetCode.INCORRECT_TARGET

        if inviter_telegram_id:
            inviter_user = self.get_by_id(inviter_telegram_id)
            if not inviter_user:
                return RetCode.NO_INVITER
            inviter_id = inviter_user.id
        else:
            inviter_id = None

        user = User(telegram_id, first_name, last_name, user_name, canInvite, updateLinksTime, chat_id, inviter_id, language_code, is_premium, ref_links)
        user.wallet = Wallet()
        self.__session__.add(user)
        self.__session__.commit()

        return RetCode.OK

    def ban_user(self, telegram_id: int) -> RetCode:
        if not self.get_by_id(telegram_id):
            return RetCode.INCORRECT_TARGET
        user = self.get_by_id(telegram_id)
        user.banned = True
        self.__session__.add(user)
        self.__session__.commit()
        return RetCode.OK

    def change_user_language(self, telegram_id: int, new_lang: str) -> RetCode:
        if not self.get_by_id(telegram_id):
            return RetCode.INCORRECT_TARGET
        assert new_lang in {'RUS', 'ENG', 'CHI'}
        user = self.get_by_id(telegram_id)
        user.languageCode = new_lang
        self.__session__.add(user)
        self.__session__.commit()
        return RetCode.OK

    def set_user_inviter_id(self, invited: int, referal_id: int):
        user = self.get_by_id(invited)
        assert user is not None
        user.referralId = referal_id
        self.__session__.add(user)
        self.__session__.commit()

    def set_user_group(self, user_tg_id:int, chat_id:int):
        user = self.get_by_id(user_tg_id)
        assert user is not None
        user.chat_id = chat_id
        self.__session__.add(user)
        self.__session__.commit()

    def change_ref_links_count(self, telegramId: int, new_ref_links_count: int):
        user = self.get_by_id(telegramId)
        assert user is not None
        user.refLinks = new_ref_links_count
        self.__session__.add(user)
        self.__session__.commit()

    def getUpdateLinksTime(self, telegramId: int):
        user = self.get_by_id(telegramId)
        return user.updateLinksTime

    def setUpdateLinksTime(self, telegramId, dateTime):
        user = self.get_by_id(telegramId)
        user.updateLinksTime = dateTime
        self.__session__.commit()

    def getUserReferalId(self, telegramId):
        user = self.get_by_id(telegramId)
        return user.referralId


    def getUserProfitPercent(self, telegramId):
        user = self.get_by_id(telegramId)
        return user.profitPercent

    def all_users(self) -> list[User]:
        return self.__session__.query(User)