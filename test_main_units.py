import unittest
import sys
import os
import datetime
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTime, Qt
from Dish import Dish
from DishBase import DishBase
from main import (
    MenuManager,
    MenuTableModel,
    MenuFormManager,
    MenuFileHandler,
    MenuWindow
)

app = QApplication(sys.argv)

class TestDish(unittest.TestCase):
    def setUp(self):
        """Подготовка тестового окружения"""
        self.sample_dish = Dish("Паста Карбонара", 450.0, datetime.time(0, 20))
    
    def test_dish_as_string(self):
        """Тестирование строкового представления блюда"""
        self.assertEqual(str(self.sample_dish), "Паста Карбонара,450.0,00:20")

class TestMenuManager(unittest.TestCase):
    def setUp(self):
        """Подготовка тестового окружения"""
        self.manager = MenuManager()
        self.sample_dish = Dish("Паста Карбонара", 450.0, datetime.time(0, 20))

    def test_add_dish(self):
        """Тестирование добавления блюда"""
        self.manager.add_dish(self.sample_dish)
        self.assertEqual(len(self.manager.dishes), 1)
        self.assertIsInstance(self.manager.dishes[0], Dish)

    def test_delete_dish(self):
        """Тестирование удаления блюда"""
        self.manager.add_dish(self.sample_dish)
        self.manager.delete_dish(0)
        self.assertEqual(len(self.manager.dishes), 0)

    def test_clear_menu(self):
        """Тестирование очистки меню"""
        self.manager.add_dish(self.sample_dish)
        self.manager.clear_menu()
        self.assertEqual(len(self.manager.dishes), 0)

    def test_get_menu(self):
        """Тестирование получения копии меню"""
        self.manager.add_dish(self.sample_dish)
        dishes = self.manager.get_menu()
        self.assertEqual(len(dishes), 1)
        self.assertEqual(dishes[0].name, "Паста Карбонара")

class TestMenuTableModel(unittest.TestCase):
    def setUp(self):
        """Подготовка тестового окружения"""
        self.manager = MenuManager()
        self.model = MenuTableModel(self.manager)
        self.sample_dish = Dish("Паста Карбонара", 450.0, datetime.time(0, 20))

    def test_row_count(self):
        """Тестирование количества строк"""
        self.assertEqual(self.model.rowCount(), 0)
        self.manager.add_dish(self.sample_dish)
        self.assertEqual(self.model.rowCount(), 1)

    def test_column_count(self):
        """Тестирование количества столбцов"""
        self.assertEqual(self.model.columnCount(), 3)

    def test_data_display(self):
        """Тестирование отображения данных"""
        self.manager.add_dish(self.sample_dish)
        index = self.model.index(0, 0)
        self.assertEqual(self.model.data(index), "Паста Карбонара")
        
        index = self.model.index(0, 1)
        self.assertEqual(self.model.data(index), "450.00")
        
        index = self.model.index(0, 2)
        self.assertEqual(self.model.data(index), "00:20")

    def test_header_data(self):
        """Тестирование заголовков таблицы"""
        self.assertEqual(self.model.headerData(0, Qt.Orientation.Horizontal), "Название")
        self.assertEqual(self.model.headerData(1, Qt.Orientation.Horizontal), "Цена")
        self.assertEqual(self.model.headerData(2, Qt.Orientation.Horizontal), "Время приготовления")

class TestMenuFormManager(unittest.TestCase):
    def setUp(self):
        """Подготовка тестового окружения"""
        self.mock_layout = MagicMock()
        self.form_manager = MenuFormManager(self.mock_layout)

    @patch('PyQt6.QtWidgets.QLineEdit', autospec=True)
    @patch('PyQt6.QtWidgets.QDoubleSpinBox', autospec=True)
    @patch('PyQt6.QtWidgets.QTimeEdit', autospec=True)
    def test_get_form_values(self, mock_time, mock_spin, mock_line):
        """Тестирование получения значений формы"""
        mock_line.text.return_value = "Паста Карбонара"
        mock_spin.value.return_value = 450.0
        mock_time.time.return_value.toPyTime.return_value = datetime.time(0, 20)
        self.form_manager.name_edit = mock_line
        self.form_manager.price_edit = mock_spin
        self.form_manager.prep_time_edit = mock_time
        name, price, prep_time = self.form_manager.get_form_values()
        self.assertEqual(name, "Паста Карбонара")
        self.assertEqual(price, 450.0)
        self.assertEqual(prep_time, datetime.time(0, 20))

class TestMenuFileHandler(unittest.TestCase):
    def setUp(self):
        """Подготовка тестового окружения"""
        self.temp_file = "temp_test_file.txt"
        self.sample_dish = Dish("Паста Карбонара", 450.0, datetime.time(0, 20))
        self.logger = MagicMock()

    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_save_and_load_menu(self):
        """Тестирование сохранения и загрузки меню"""
        dishes = [self.sample_dish]
        file_handler = MenuFileHandler(self.logger)
        file_handler.save_menu(dishes, self.temp_file)
        
        loaded_dishes = file_handler.load_menu(self.temp_file)
        self.assertEqual(len(loaded_dishes), 1)
        self.assertIsInstance(loaded_dishes[0], Dish)
        self.assertEqual(loaded_dishes[0].name, "Паста Карбонара")
        self.assertEqual(loaded_dishes[0].price, 450.0)

    def test_load_empty_name(self):
        """Тестирование загрузки блюда с пустым названием"""
        file_handler = MenuFileHandler(self.logger)
        with open(self.temp_file, 'w', encoding='utf-8') as file:
            file.write(",450.0,00:20\n")
        loaded_dishes = file_handler.load_menu(self.temp_file)
        self.assertEqual(len(loaded_dishes), 0)
        self.logger.log_message.assert_called_once()

    def test_load_invalid_price(self):
        """Тестирование загрузки блюда с отрицательной ценой"""
        file_handler = MenuFileHandler(self.logger)
        with open(self.temp_file, 'w', encoding='utf-8') as file:
            file.write("Паста Карбонара,-450.0,00:20\n")
        loaded_dishes = file_handler.load_menu(self.temp_file)
        self.assertEqual(len(loaded_dishes), 0)
        self.logger.log_message.assert_called_once()

    def test_load_invalid_time(self):
        """Тестирование загрузки блюда с некорректным временем"""
        file_handler = MenuFileHandler(self.logger)
        with open(self.temp_file, 'w', encoding='utf-8') as file:
            file.write("Паста Карбонара,450.0,25:20\n")
        loaded_dishes = file_handler.load_menu(self.temp_file)
        self.assertEqual(len(loaded_dishes), 0)
        self.logger.log_message.assert_called_once()

class TestMenuWindow(unittest.TestCase):
    def setUp(self):
        """Подготовка тестового окружения"""
        self.window = MenuWindow()

    def test_initial_state(self):
        """Тестирование начального состояния окна"""
        self.assertEqual(self.window.windowTitle(), "Меню ресторана")
        self.assertEqual(len(self.window.menu_manager.dishes), 0)
        
    def test_add_dish(self):
        """Тестирование добавления блюда"""
        self.window.form_manager.name_edit.setText("Паста Карбонара")
        self.window.form_manager.price_edit.setValue(450.0)
        self.window.form_manager.prep_time_edit.setTime(QTime(0, 20))
        self.window.add_dish()
        self.assertEqual(len(self.window.menu_manager.dishes), 1)
        self.assertEqual(self.window.menu_manager.dishes[0].name, "Паста Карбонара")

    @patch.object(QMessageBox, 'warning')
    def test_add_dish_empty_name(self, mock_warning):
        """Тестирование добавления блюда с пустым названием"""
        self.window.form_manager.name_edit.setText("")
        self.window.add_dish()
        self.assertEqual(len(self.window.menu_manager.dishes), 0)
        mock_warning.assert_called_once()

    @patch.object(QMessageBox, 'warning')
    def test_add_dish_invalid_price(self, mock_warning):
        """Тестирование добавления блюда с отрицательной ценой"""
        self.window.form_manager.name_edit.setText("Паста Карбонара")
        self.window.form_manager.price_edit.setValue(-450.0)
        self.window.add_dish()
        self.assertEqual(len(self.window.menu_manager.dishes), 0)
        mock_warning.assert_called_once()

    @patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes)
    def test_delete_dish(self, mock_question):
        """Тестирование удаления блюда"""
        test_dish = Dish("Паста Карбонара", 450.0, datetime.time(0, 20))
        self.window.menu_manager.add_dish(test_dish)
        self.window.table_view = MagicMock()
        self.window.table_view.currentIndex.return_value.isValid.return_value = True
        self.window.table_view.currentIndex.return_value.row.return_value = 0
        self.window.delete_dish()
        self.assertEqual(len(self.window.menu_manager.dishes), 0)

    @patch.object(MenuFileHandler, 'save_menu')
    @patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=("test.txt", None))
    def test_save_menu(self, mock_dialog, mock_save):
        """Тестирование сохранения меню"""
        self.window.save_menu()
        mock_save.assert_called_once()

    @patch.object(MenuFileHandler, 'load_menu')
    @patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("test.txt", None))
    @patch.object(QMessageBox, 'information')
    def test_load_menu_success(self, mock_info, mock_dialog, mock_load):
        """Тестирование успешной загрузки меню"""
        test_dish = Dish("Паста Карбонара", 450.0, datetime.time(0, 20))
        mock_load.return_value = [test_dish]
        self.window.load_menu()
        self.assertEqual(len(self.window.menu_manager.dishes), 1)
        mock_info.assert_called_once()

    @patch.object(MenuFileHandler, 'load_menu', side_effect=Exception("Тестовая ошибка"))
    @patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("test.txt", None))
    @patch.object(QMessageBox, 'critical')
    def test_load_menu_failure(self, mock_critical, mock_dialog, mock_load):
        """Тестирование неуспешной загрузки меню"""
        self.window.load_menu()
        mock_critical.assert_called_once()

if __name__ == '__main__':
    unittest.main()