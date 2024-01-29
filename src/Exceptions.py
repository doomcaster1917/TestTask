class NotRightCurName(Exception):
    def __str__(self):
        return "Not right currency name"

class MatchingDuplicateCurs(Exception):
    def __str__(self):
        return "Attemp to exchange duplicate currencies"