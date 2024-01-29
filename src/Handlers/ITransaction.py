import abc

class ITransaction:
    @abc.abstractmethod
    def serialize_data(self) -> dict[str]:
        """Вывести все данные о транзакции"""
        raise NotImplementedError