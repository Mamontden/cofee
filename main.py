import sqlite3
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.cur = self.con.cursor()
        self.create_table()
        self.load_coffee_data()

        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button.clicked.connect(self.open_edit_dialog)

    def open_add_dialog(self):
        dialog = AddEditCoffeeDialog(self.con)
        if dialog.exec():
            self.load_coffee_data()

    def open_edit_dialog(self):
        current_row = self.tableWidget.currentRow()
        if current_row != -1:
            coffee_id = self.tableWidget.item(current_row, 0).text()
            coffee_data = self.cur.execute("SELECT * FROM coffee WHERE id=?", (coffee_id,)).fetchone()
            dialog = AddEditCoffeeDialog(self.con, coffee_data)
            if dialog.exec():
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
            self.tableWidget.setColumnCount(len(db[0]))
            self.tableWidget.setRowCount(len(db))
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Название сорта", "Степень обжарки", "Тип",
                                                        "Описание вкуса", "Цена", "Объем упаковки"])
            self.tableWidget.setColumnHidden(0, True)

            for i, coffee in enumerate(db):
                for j, value in enumerate(coffee):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
        else:
            print("Нет данных для отображения, добавляем примерные данные...")
            self.add_sample_data()
            self.load_coffee_data()

    def add_sample_data(self):
        sample_data = [
            ('Эспрессо', 'Сильная', 'Молотый', 'Вкусный', 500, '250г'),
            ('Капучино', 'Средняя', 'В зернах', 'Кремовый', 600, '500г'),
            ('Американо', 'Легкая', 'Молотый', 'Мягкий', 450, '200г')
        ]

        for item in sample_data:
            self.cur.execute(
                "INSERT INTO coffee (name, roasting, type, taste, price, package) VALUES (?, ?, ?, ?, ?, ?)", item
            )
        self.con.commit()

    def closeEvent(self, event):
        self.con.close()
        event.accept()

class AddEditCoffeeDialog(QDialog):
    def __init__(self, db_connection, coffee_data=None):
        super().__init__()
        uic.loadUi("addEditCoffeeForm.ui", self)
        self.con = db_connection
        self.cur = self.con.cursor()
        self.coffee_data = coffee_data

        if coffee_data:
            self.populate_fields(coffee_data)
            self.save_button.clicked.connect(self.edit_coffee)
        else:
            self.save_button.clicked.connect(self.add_coffee)
        self.cancel_button.clicked.connect(self.reject)

    def populate_fields(self, coffee_data):
        self.name_input.setText(coffee_data[1])
        self.roasting_input.setText(coffee_data[2])
        self.type_input.setText(coffee_data[3])
        self.taste_input.setText(coffee_data[4])
        self.price_input.setText(str(coffee_data[5]))
        self.package_input.setText(coffee_data[6])

    def add_coffee(self):
        try:
            self.cur.execute(
                "INSERT INTO coffee (name, roasting, type, taste, price, package) VALUES (?, ?, ?, ?, ?, ?)",
                (self.name_input.text(), self.roasting_input.text(), self.type_input.text(),
                 self.taste_input.text(), int(self.price_input.text()), self.package_input.text())
            )
            self.con.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")

    def edit_coffee(self):
        try:
            self.cur.execute(
                "UPDATE coffee SET name=?, roasting=?, type=?, taste=?, price=?, package=? WHERE id=?",
                (self.name_input.text(), self.roasting_input.text(), self.type_input.text(),
                 self.taste_input.text(), int(self.price_input.text()), self.package_input.text(),
                 self.coffee_data[0])
            )
            self.con.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())