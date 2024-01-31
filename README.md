# TestTaskForVacancy

### Language-notification:
Поскольку компания российская, документация и комментарии будут на русском языке. При необходимости могу быстро перевести на английский.

### Структура кода:
Код, находящийся в проекте, разделён:
   - На папку Handlers. В этой папке находятся модули, работающие с базой данных. Каждый из них отвечает за свою логику: wallet-, user-, transactions- handlers. Ret code и Itransacrion - дополнительные модули, используемые в работе хэндлеров.
   - Модуль DatabaseModels.py ответствен структуру таблиц базы данных.
   - UserIntarface.py ответствен за пользовательский интерфейс. 
   - TaskMethods.py - модуль, содержащий класс Task. Класс содержит методы, которые используются интерфейсом. Сам использует методы классов папки Handlers для получения информации.
   - Дополнительные методы tools, config и main. Tools содержит методы-помощники для класса Task, config - данные конфигурации, main - запускает инициализацию базы данных и включает интерфейс пользователя.

### Слои программы:
Программа содержит 3 слоя абстрации. UserInterface > TaskMethods > Handlers. IserInterface не может использовать методы Handlers и обращается к данным с помощи прослойки TaskMethods.

### Понятия купли/продажи.
 В коде эти понятия используются как абстрации над операцией обмена - InChange, созданные для интерфейса пользователя.
 Классы Task и UserInterface используют эти сущности в следующих значениях:
    - buy_operation - операция обмена RUB на криптовалюты.
    - sell_operation - операция обмана криптовалюты на RUB.

### TaskMethods
Модуль содержит в себе 4 типа методов: tools, db-init, db, calculate. 


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
    -  Добавление  продаваемой валюты в депозит (table Deposit) и подтверждение операции.
    -  Удаление продаваемой валюты из кошелька (table Wallet).
    -  Добавление обменной операции в таблицу внутренних обменных операций и подтверждение операции(table InternalExchange).
    -  Добавление купленной валюты в кошелёк(table Wallet).
    -  Удаление продаваемой валюты из депозита
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

### !!!Документация написана не до конца. До 22:00 31.01.2024 она будет дописана!!!
