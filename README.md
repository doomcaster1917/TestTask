# TestTaskForVacancy

### Language-notification:
Поскольку компания российская, документация и комментарии будут на русском языке. При необходимости могу быстро перевести на английский.

### Запуск сервиса:
Для запуска необходимо заполнить поля .env-файла, далее запустить src/main.py  

### Структура кода:
Код, находящийся в проекте, разделён:
   - На папку Handlers. В этой папке находятся модули, работающие с базой данных. Каждый из них отвечает за свою логику: wallet-, user-, transactions- handlers. Ret code и Itransacrion - дополнительные модули, используемые в работе хэндлеров.
   - Модуль DatabaseModel.py ответствен структуру таблиц базы данных.
   - UserIntarface.py ответствен за пользовательский интерфейс. 
   - TaskMethods.py - модуль, содержащий класс Task. Класс содержит методы, которые используются интерфейсом. Сам использует методы классов папки Handlers для получения информации.
   - Дополнительные методы tools, config и main. Tools содержит методы-помощники для класса Task, config - данные конфигурации, main - запускает инициализацию базы данных и включает интерфейс пользователя.

### Слои программы:
Программа содержит 3 слоя абстрации. UserInterface > TaskMethods > Handlers. IserInterface не может использовать методы Handlers и обращается к данным с помощи прослойки TaskMethods.
TaskMethods, по сути, является Middleware сервиса.

### Документация DatabaseModel и Handlers (то есть приложенного к заданию кода):
Документация в виде схем с описаниями: https://miro.com/app/board/uXjVN0GBRzE=/?share_link_id=668176223358 \
В документации описаны модели базы данных и класс TasksHandler.
![Screenshot from 2024-01-31 21-38-26](https://github.com/doomcaster1917/TestTask/assets/113614995/52ce5cd3-0054-4572-9c91-6d8d33357d5a)


### Понятия купли/продажи.
 В коде эти понятия используются как абстрации над операцией обмена - InChange, созданные для интерфейса пользователя.
 Классы Task и UserInterface используют эти сущности в следующих значениях: \
    - buy_operation - операция обмена RUB на криптовалюты. \
    - sell_operation - операция обмана криптовалюты на RUB. \

### class Taks from module TaskMethods
Класс содержит в себе 4 типа методов: tools, db-init, db, calculate. 
Класс принимает в качестве аргументов TransactionHandler, UserHandler, WalletHandler и далее использует их в качестве self-аттрибутов.

```
    get_currency_price(currency_from: str, currency_to: str) -> Decimal   
```
Принимает на вход 2 валюты и возвращает одну валюту в исчислении другой. К примеру, при currency_from = RUB и currency_to = BTC
метод вернёт стоимость BTC в рублях. В зависимости от валюты метод возвращает dectimal с разным количеством нулей после точки.
    
Примечание: метод возвращает для RUB значение dectimal c 16 знаками после точки. Это обусловлено необходимостью выражать RUB в других валютах.

```
    in_change_currency(date_time:str, telegram_id: int, currency_from: str, currency_to: str,
                           value_from: Decimal, value_to: Decimal) -> None: 
```
Использует методы класса TasksHandler для совершения операций обмена. Последовательность действией метода следующая:
   1. Добавление  продаваемой валюты в депозит (table Deposit) и подтверждение операции 
   2. Удаление продаваемой валюты из кошелька (table Wallet)
   3. Добавление обменной операции в таблицу внутренних обменных операций и подтверждение операции(table InternalExchange).
   4. Добавление купленной валюты в кошелёк(table Wallet).
   5. Удаление продаваемой валюты из депозита <br>
Примечание: подтверждение (approve) операций происходит автоматически, поскольку такое требование к интерфейсу не предусмотрено в задании.     
    
```
    exchanges_filter() -> dict:
```
Извлекает все обменные операции пользователя по его telegram_id с помощью метода TasksHandler.getExchanges()
Возвращает словарь с ключами buy_operations и sell_operations (см. абстракции купли/продажи).

```
    calculate_transactions_profits() -> list:
```
Использует exchanges_filter() для получения операций покупки и продажи криптовалюты - buy_operations и sell_operations.
Находит к каждой операции продажи (crypto_currency>RUB) последнюю операцию покупки этой криптовалюты и на основании разницы 
в стоимости криптовалюты (исчисляемой в рублях) определяет размер прибыли/убытка этой операции.
Возвращает массив list(dict) операций с указанным profit в каждой операции.



```
    get_last_purchase_of_currency(buy_operations: list, currency: str) -> dict:
```

Принимает на вход массив операций покупки и валюту. Находит по заданной валюте последнюю операцию покупки путём сравнения timestamp операций.
Возвращает словарь данных этой операции.
Метод используется в функции calculate_transactions_profits() при вычислении разницы в цене валюты на момент покупки и момент продажи.


### class UserInterface from module UserInterface

Все методы этого класса похожи друг на друга и если их описывать, то документация разрастётся до неприличных размеров и её просто не захочется дальше читать.
Различие методов состоит в том, что все методы класса разделяются на 3 типа: buy, sell, calculation. Каждый тип методов отвечает за направление, соответствующее своему названию.
Взаимодействие с пользователем в методах происходит при помощи базового метода input("prompt") и ветви условий.
В методах реализовано:
- Форматирование выводимых данных. В том числе форматирование в dectimal-значениях количество знаков после точки через :.f\
- Форматирование временных значений формата timestamp в формат %Y-%m-%d %H:%M:%S часового пояса Europe/Moscow    
- Проверка на ошибочно введённые значения. Если пользователь введёт буквы вместо числового значения, неверное название валюты и тд., то система вернёт его к начальной точке интерфейса.\
- Проверка баланса. Если пользователь захочет купить или продать валюту при недостаточном для этого балансе, система оповестит его и вернёт к вводу значения.\
    



