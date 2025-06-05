import sys
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableView, QPushButton, QLineEdit, QTimeEdit, QDoubleSpinBox,
                             QLabel, QMessageBox, QFileDialog)
from PyQt6.QtCore import QTime, Qt, QAbstractTableModel, QModelIndex
from Dish import Dish
from DishBase import DishBase
import datetime
import os.path

class Logger:
    """Класс для управления логированием ошибок"""
    
    def __init__(self):
        """Инициализация папки для логов"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
    def log_message(self, level: str, message: str, filename = f"{datetime.datetime.now().strftime('%d-%m-%Y')}.log") -> None:
        """
        Запись сообщения в лог-файл
        
        Args:
            level (str): Уровень лога (ОШИБКА, ПРЕДУПРЕЖДЕНИЕ...)
            message (str): Сообщение для записи
            filename (str): Имя лог-файла (по умолчанию текущая дата)
        """
        if not os.path.exists(f"logs/{filename}"):
            with open(f"logs/{filename}", "w", encoding='utf-8') as file:
                file.write(f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} {level} {message}\n")
        else:
            with open(f"logs/{filename}", "a", encoding='utf-8') as file:
                file.write(f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} {level} {message}\n")

class MenuManager:
    """Класс для управления меню ресторана"""
    
    def __init__(self):
        """Инициализация пустого меню"""
        self.dishes = []
    
    def add_dish(self, dish: DishBase) -> None:
        """
        Добавление блюда в меню
        
        Args:
            dish (DishBase): Блюдо для добавления
        """
        self.dishes.append(dish)
    
    def delete_dish(self, index: int) -> None:
        """
        Удаление блюда по индексу
        
        Args:
            index (int): Индекс блюда
        """
        if 0 <= index < len(self.dishes):
            del self.dishes[index]
    
    def clear_menu(self) -> None:
        """Очистка всего меню"""
        self.dishes = []
    
    def get_menu(self) -> list[DishBase]:
        """Получение копии меню"""
        return self.dishes.copy()

class MenuTableModel(QAbstractTableModel):
    """Модель Qt для отображения меню в таблице"""
    
    def __init__(self, menu_manager: MenuManager, parent=None):
        """
        Инициализация модели таблицы
        
        Args:
            menu_manager (MenuManager): Менеджер меню
            parent: Родительский объект Qt
        """
        super().__init__(parent)
        self.menu_manager = menu_manager
        self.headers = ["Название", "Цена", "Время приготовления"]
    
    def columnCount(self, parent=None) -> int:
        """Получение количества столбцов"""
        return len(self.headers)
    
    def rowCount(self, parent=None) -> int:
        """Получение количества строк"""
        return len(self.menu_manager.get_menu())
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> str|None:
        """
        Получение данных для отображения в таблице
        
        Args:
            index (QModelIndex): Индекс ячейки
            role (Qt.ItemDataRole): Роль данных Qt
        
        Returns:
            str|None: Данные ячейки или None
        """
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        
        dish = self.menu_manager.get_menu()[index.row()]
        
        if index.column() == 0:
            return dish.name
        elif index.column() == 1:
            return f"{dish.price:.2f}"
        elif index.column() == 2:
            return dish.prep_time.strftime("%H:%M")
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole) -> str|None:
        """
        Получение заголовков таблицы
        
        Args:
            section (int): Номер секции
            orientation (Qt.Orientation): Ориентация таблицы (вертикальная/горизонтальная)
        
        Returns:
            str|None: Заголовок или None
        """
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

class MenuFormManager:
    """Класс для управления полями формы ввода данных о блюде"""
    
    def __init__(self, form_layout: QHBoxLayout):
        """
        Инициализация менеджера формы
        
        Args:
            form_layout (QHBoxLayout): Макет для полей формы
        """
        self.form_layout = form_layout
        self.name_edit = QLineEdit()
        self.price_edit = QDoubleSpinBox()
        self.prep_time_edit = QTimeEdit()
        self.init_form_fields()
    
    def init_form_fields(self) -> None:
        """Инициализация полей формы для блюда"""
        # Поле для названия блюда
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("Название блюда"))
        self.name_edit.setPlaceholderText("Например, Паста Карбонара")
        name_layout.addWidget(self.name_edit)
        self.form_layout.addLayout(name_layout)
        
        # Поле для цены
        price_layout = QVBoxLayout()
        price_layout.addWidget(QLabel("Цена (руб)"))
        self.price_edit.setMinimum(0.1)
        self.price_edit.setMaximum(10000.0)
        self.price_edit.setSingleStep(50.0)
        price_layout.addWidget(self.price_edit)
        self.form_layout.addLayout(price_layout)
        
        # Поле для времени приготовления
        time_layout = QVBoxLayout()
        time_layout.addWidget(QLabel("Время приготовления"))
        self.prep_time_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.prep_time_edit)
        self.form_layout.addLayout(time_layout)
    
    def get_form_values(self) -> tuple[str, float, QTime]:
        """
        Получение значений из полей формы
        
        Returns:
            tuple[str, float, QTime]: Название, цена и время приготовления
        """
        return self.name_edit.text().strip(), self.price_edit.value(), self.prep_time_edit.time()

class MenuFileHandler:
    """Класс для обработки сохранения и загрузки меню"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def save_menu(self, dishes: list[DishBase], filename: str) -> None:
        """
        Сохранение меню в файл
        
        Args:
            dishes (list[DishBase]): Список блюд
            filename (str): Путь к файлу
        """
        with open(filename, 'w', encoding='utf-8') as file:
            for dish in dishes:
                file.write(str(dish) + "\n")
    
    def load_menu(self, filename: str) -> list[DishBase]:
        """
        Загрузка меню из файла
        
        Args:
            filename (str): Путь к файлу
            
        Returns:
            list[DishBase]: Список блюд
        """
        dishes = []
        
        with open(filename, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    name, price_str, time_str = line.split(',')
                    # Валидация названия
                    if not name:
                        raise ValueError("Название блюда не может быть пустым")
                    # Валидация цены
                    price = float(price_str)
                    if price <= 0:
                        raise ValueError(f"Цена должна быть положительной: {price_str}")
                    # Валидация времени приготовления
                    try:
                        hours, minutes = map(int, time_str.split(':'))
                        if not (0 <= hours < 24 and 0 <= minutes < 60):
                            raise ValueError("Некорректное время")
                        prep_time = datetime.time(hours, minutes)
                    except ValueError:
                        raise ValueError(f"Неверный формат времени: {time_str}")
                    
                    dishes.append(Dish(name, price, prep_time))
                except Exception as e:
                    self.logger.log_message("ОШИБКА", f"Не удалось разобрать строку {line_number}: {line}. Ошибка: {str(e)}")
        return dishes

class MenuWindow(QMainWindow):
    """Главное окно приложения для управления меню ресторана"""
    
    def __init__(self):
        """Инициализация главного окна"""
        super().__init__()
        self.setWindowTitle("Меню ресторана")
        self.setGeometry(100, 100, 800, 600)
        
        # Инициализация компонентов
        self.menu_manager = MenuManager()
        self.logger = Logger()
        self.file_handler = MenuFileHandler(self.logger)
        
        # Создание интерфейса
        self.init_ui()
    
    def init_ui(self) -> None:
        """Инициализация пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Создание таблицы
        self.table_view = QTableView()
        self.table_model = MenuTableModel(self.menu_manager)
        self.table_view.setModel(self.table_model)
        layout.addWidget(self.table_view)
        
        # Создание формы
        form_layout = QHBoxLayout()
        
        # Инициализация менеджера формы
        self.form_manager = MenuFormManager(form_layout)
        
        # Кнопка добавления блюда
        self.add_button = QPushButton("Добавить блюдо")
        self.add_button.clicked.connect(self.add_dish)
        form_layout.addWidget(self.add_button)
        
        layout.addLayout(form_layout)
        
        # Макет для кнопок управления
        button_layout = QHBoxLayout()
        
        # Кнопка загрузки
        self.load_button = QPushButton("Загрузить меню")
        self.load_button.clicked.connect(self.load_menu)
        button_layout.addWidget(self.load_button)
        
        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить меню")
        self.save_button.clicked.connect(self.save_menu)
        button_layout.addWidget(self.save_button)
        
        # Кнопка удаления
        self.delete_button = QPushButton("Удалить выбранное")
        self.delete_button.clicked.connect(self.delete_dish)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
    
    def add_dish(self) -> None:
        """Добавление нового блюда на основе данных формы"""
        name, price, prep_time = self.form_manager.get_form_values()
        
        # Валидация названия
        if not name:
            QMessageBox.warning(self, "Предупреждение", "Название блюда не может быть пустым!")
            self.logger.log_message("ПРЕДУПРЕЖДЕНИЕ", "Попытка добавить блюдо с пустым названием")
            return
        
        # Валидация цены
        if price <= 0:
            QMessageBox.warning(self, "Предупреждение", "Цена должна быть положительной!")
            self.logger.log_message("ПРЕДУПРЕЖДЕНИЕ", f"Неверная цена: {price}")
            return
        
        dish = Dish(name, price, prep_time.toPyTime())
        self.menu_manager.add_dish(dish)
        self.table_model.layoutChanged.emit()
    
    def delete_dish(self) -> None:
        """Удаление выбранного блюда"""
        selected = self.table_view.currentIndex()
        if not selected.isValid():
            QMessageBox.warning(self, "Предупреждение", "Выберите блюдо для удаления!")
            self.logger.log_message("ПРЕДУПРЕЖДЕНИЕ", "Попытка удаления блюда без выбора")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение удаления", 
            "Вы уверены, что хотите удалить это блюдо?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.menu_manager.delete_dish(selected.row())
            self.table_model.layoutChanged.emit()
    
    def save_menu(self) -> None:
        """Сохранение меню в файл"""
        filename, _ = QFileDialog.getSaveFileName(
            None, "Сохранить меню", ".", "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        if filename:
            self.file_handler.save_menu(
                self.menu_manager.get_menu(),
                filename
            )
    
    def load_menu(self) -> None:
        """Загрузка меню из файла"""
        filename, _ = QFileDialog.getOpenFileName(
            None, "Открыть меню", ".", "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        if filename:
            try:
                dishes = self.file_handler.load_menu(filename)
                self.menu_manager.clear_menu()
                for dish in dishes:
                    self.menu_manager.add_dish(dish)
                self.table_model.layoutChanged.emit()
                QMessageBox.information(self, "Успех", "Меню успешно загружено!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")
                self.logger.log_message("ОШИБКА", f"Не удалось загрузить файл: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MenuWindow()
    window.show()
    sys.exit(app.exec())