from datetime import time

class DishBase:
    """Базовый класс для блюд в меню"""
    
    def __init__(self, name: str, price: float, prep_time: time):
        """
        Инициализация блюда
        
        Args:
            name (str): Название блюда
            price (float): Цена блюда
            prep_time (time): Время приготовления
        """
        self.__name = name
        self.__price = price
        self.__prep_time = prep_time
    
    @property
    def name(self) -> str:
        """Получить название блюда"""
        return self.__name

    @property
    def price(self) -> float:
        """Получить цену блюда"""
        return self.__price

    @property
    def prep_time(self) -> time:
        """Получить время приготовления"""
        return self.__prep_time

    def __str__(self) -> str:
        """Строковое представление блюда (должно быть реализовано в подклассах)"""
        raise NotImplementedError()