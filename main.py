import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.cur = self.con.cursor()
        self.create_table()
        self.load_coffee_data()

    def create_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS coffee (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            roasting TEXT,
                            type TEXT,
                            taste TEXT,
                            price INTEGER,
                            package TEXT)""")
        self.con.commit()

    def load_coffee_data(self):
        self.cur.execute("SELECT * FROM coffee")
        db = self.cur.fetchall()
        if db:
            self.tableWidget.setColumnCount(len(db[0]) - 1)
            self.tableWidget.setRowCount(len(db))
            self.tableWidget.setHorizontalHeaderLabels(["Название сорта", "Степень обжарки", "Тип", "Описание вкуса",
                                                        "Цена", "Объем упаковки"])

            for i, coffee in enumerate(db):
                for j, value in enumerate(coffee[1:]):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
        else:
            print("Нет данных для отображения")
            self.add_sample_data()

    def add_sample_data(self):  # создаем пример из 3 строк. Для проверки
        sample_data = [
            ('Эспрессо', 'Сильная', 'Молотый', 'Вкусный', 500, '250г'),
            ('Капучино', 'Средняя', 'В зернах', 'Кремовый', 600, '500г'),
            ('Американо', 'Легкая', 'Молотый', 'Мягкий', 450, '200г')
        ]

        self.cur.execute("SELECT COUNT(*) FROM coffee")
        if self.cur.fetchone()[0] == 0:
            for item in sample_data:
                self.cur.execute(
                    "INSERT INTO coffee (name, roasting, type, taste, price, package) VALUES (?, ?, ?, ?, ?, ?)", item
                )
            self.con.commit()

    def closeEvent(self, event):
        self.con.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
