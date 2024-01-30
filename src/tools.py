from decimal import  Decimal, ROUND_DOWN
from typing import Union

# precission and scale hints:
# btcBalance = Column(DECIMAL(32, 8))
# ethBalance = Column(DECIMAL(32, 18))
# trxBalance = Column(DECIMAL(32, 16))
# tonBalance = Column(DECIMAL(32, 9))
# xmrBalance = Column(DECIMAL(32, 12))
# usdtBalance = Column(DECIMAL(32, 2))
# rubBalance = Column(DECIMAL(32, 2))

def dectimal_converter(value: Union[str, float], currency: str):

    if currency == "RUB" or currency == "USDT":
        dectimal_to = Decimal(value).quantize(Decimal('.0000000000000000'), rounding=ROUND_DOWN)
    elif currency == "BTC":
        dectimal_to = Decimal(value).quantize(Decimal('.00000000'), rounding=ROUND_DOWN)
    elif currency == "ETH":
        dectimal_to = Decimal(value).quantize(Decimal('.000000000000000000'), rounding=ROUND_DOWN)
    elif currency == "TRX":
        dectimal_to = Decimal(value).quantize(Decimal('.0000000000000000'), rounding=ROUND_DOWN)
    elif currency == "TON":
        dectimal_to = Decimal(value).quantize(Decimal('.000000000'), rounding=ROUND_DOWN)
    elif currency == "XMR":
        dectimal_to = Decimal(value).quantize(Decimal('.000000000000'), rounding=ROUND_DOWN)
    else:
        dectimal_to = Decimal(value).quantize(Decimal('.0000000000000000'), rounding=ROUND_DOWN)
    return dectimal_to

# В программе возникает необходимость выразить рубль в цене криптовалюты (к примеру, BTC)
# и в этом случае RUB может быть выражен dectimal-числом с большим количеством нулей после точки
def revers_dectimal_converter(value: Union[str, float]):
    return Decimal(value).quantize(Decimal('.0000000000000000'), rounding=ROUND_DOWN)