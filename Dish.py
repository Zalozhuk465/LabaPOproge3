from datetime import time
from DishBase import DishBase

class Dish(DishBase):
    """Класс для представления блюда в меню"""
    
    def __init__(self, name: str, price: float, prep_time: time):
        """
        Инициализация блюда
        
        Args:
            name (str): Название блюда
            price (float): Цена блюда
            prep_time (time): Время приготовления
        """
        super().__init__(name, price, prep_time)
    
    def __str__(self) -> str:
        """Строковое представление блюда"""
        return f"{self.name},{self.price},{self.prep_time.strftime('%H:%M')}"