import sys
import datetime
import sqlite3
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem, QMessageBox

from task_desc_ui_v2 import Ui_Form_Task
from main_ui_v2 import Ui_Form


class Window(QWidget, Ui_Form):
    def __init__(self):
        super(Window, self).__init__()
        # loadUi("ui/main.ui", self)

        # self.ui = Ui_Form()
        self.setupUi(self)
        self.calendarWidget.selectionChanged.connect(self.calendarDateChanged)

    def act(self):
        self.updateTasks(datetime.date.today())
        self.calendarWidget.selectionChanged.connect(self.calendarDateChanged)
        self.button_save.clicked.connect(self.saveChanges)
        self.button_add.clicked.connect(self.addNewTask)
        self.button_del.clicked.connect(self.deleteElem)
        # дабл клик для заметок
        self.tasks.itemDoubleClicked.connect(self.show_d)
        self.tasks_resolved.itemDoubleClicked.connect(self.show_d)

    def task_change(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        if self.tasks.currentItem():
            curr_task = self.tasks.currentItem().text()
            date = self.calendarWidget.selectedDate().toPyDate()

            query = "SELECT task, priority FROM tasks WHERE task = ?"
            row = (curr_task,)

            result = cursor.execute(query, row).fetchone()

            self.tasks.takeItem(self.tasks.currentRow())
            self.updateTasks(date)

        self.lineEdit.setText(result[0])
        self.comboBox.setCurrentIndex(result[1])

    def calendarDateChanged(self):
        # Проверка на изменение даты в календаре
        dateSelected = self.calendarWidget.selectedDate().toPyDate()
        self.updateTasks(dateSelected)

    def updateTasks(self, date):
        # Очистка листа, подключение ДБ
        self.tasks.clear()
        self.tasks_resolved.clear()
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        # Запрос
        query = "SELECT task, completed, priority FROM tasks WHERE date = ?"
        row = (date,)
        results = cursor.execute(query, row).fetchall()
        # сортировка задач по приоритету
        results.sort(key=lambda tup: tup[2], reverse=True)

        # Возврат результата
        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            # цвет задачи в зависимости от приоритета
            if result[2] == 2:
                item.setForeground(QtGui.QColor("darkRed"))
            elif result[2] == 1:
                item.setForeground(QtGui.QColor("darkMagenta"))
            else:
                item.setForeground(QtGui.QColor("darkGreen"))

            # Проверка выполнения задачи
            if result[1] == "YES":
                item.setCheckState(QtCore.Qt.Checked)
                self.tasks_resolved.addItem(item)
            elif result[1] == "NO":
                item.setCheckState(QtCore.Qt.Unchecked)
                self.tasks.addItem(item)
            # self.tasks.addItem(item)

    def saveChanges(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        date = self.calendarWidget.selectedDate().toPyDate()
        for i in range(self.tasks.count()):
            item = self.tasks.item(i)
            task = item.text()
            if item.checkState() == QtCore.Qt.Checked:
                query = "UPDATE tasks SET completed = 'YES' where task = ? AND date = ?"
            else:
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
            row = (task, date,)
            cursor.execute(query, row)
        db.commit()

        for i in range(self.tasks_resolved.count()):
            item = self.tasks_resolved.item(i)
            task = item.text()
            if item.checkState() == QtCore.Qt.Checked:
                query = "UPDATE tasks SET completed = 'YES' where task = ? AND date = ?"
            else:
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
            row = (task, date,)
            cursor.execute(query, row)
        db.commit()

        self.updateTasks(date)

        messageBox = QMessageBox()
        messageBox.setWindowTitle("Saved")
        messageBox.setText("Changes saved.")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

    def addNewTask(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        newTask = self.lineEdit.text()
        priority = int(self.comboBox.currentText())

        if len(newTask) > 0:
            date = self.calendarWidget.selectedDate().toPyDate()

            query = "INSERT INTO tasks(task, completed, date, priority) VALUES (?,?,?,?)"
            row = (newTask, "NO", date, priority)

            cursor.execute(query, row)
            db.commit()
            self.updateTasks(date)
            self.lineEdit.clear()

        self.comboBox.setCurrentIndex(0)

    def deleteElem(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        if self.tasks.currentItem():
            delTask = self.tasks.currentItem().text()
            date = self.calendarWidget.selectedDate().toPyDate()
            query = "DELETE FROM tasks where task = ? AND date = ?"
            row = (delTask, date,)

            cursor.execute(query, row)
            db.commit()

            self.tasks.takeItem(self.tasks.currentRow())
            self.updateTasks(date)

        if self.tasks_resolved.currentItem():
            delTask = self.tasks_resolved.currentItem().text()
            date = self.calendarWidget.selectedDate().toPyDate()

            query = "DELETE FROM tasks where task = ? AND date = ?"
            row = (delTask, date,)

            cursor.execute(query, row)
            db.commit()

            self.tasks.takeItem(self.tasks.currentRow())
            self.updateTasks(date)

    def show_d(self):
        self.desc = Win()
        self.desc.show()
        self.desc.action()

    def closeEvent(self, event):
        self.desc.close()


class Win(QWidget, Ui_Form_Task):
    def __init__(self):
        super(Win, self).__init__()
        self.setupUi(self)
        self.init_task()

    def init_task(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        if window.tasks.currentItem():
            curr_task = window.tasks.currentItem().text()
        else:
            curr_task = window.tasks_resolved.currentItem().text()

        # запрос
        date = window.calendarWidget.selectedDate().toPyDate()
        query = "SELECT task, priority FROM tasks WHERE task = ?"
        row = (curr_task,)
        result = cursor.execute(query, row).fetchone()

        self.lineEdit.setText(result[0])
        self.comboBox.setCurrentIndex(result[1])

    def action(self):
        self.sc.clicked.connect(self.saveDescription)
        # Выбранная дата
        date = window.calendarWidget.selectedDate().toPyDate()
        if window.tasks.currentItem():
            # Название выбранной задачи
            task_name = window.tasks.currentItem().text()
            self.quer(task_name, date)

        elif window.tasks_resolved.currentItem():
            # Название выбранной задачи
            task_name = window.tasks_resolved.currentItem().text()
            self.quer(task_name, date)

    def quer(self, name, date):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        query = "SELECT desc FROM tasks WHERE task = ? AND date = ?"
        row = (name, date,)
        result = cursor.execute(query, row).fetchone()
        self.textEdit.setText(result[0])
        self.label.setText(name)

    def saveDescription(self):
        if window.tasks.currentItem():
            curr_item = window.tasks.currentItem().text()
        else:
            curr_item = window.tasks_resolved.currentItem().text()

        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        new_desc = self.textEdit.toPlainText()
        new_name = self.lineEdit.text()
        new_priority = int(self.comboBox.currentText())
        # # if len(newDesc) > 0:
        date = window.calendarWidget.selectedDate().toPyDate()
        query = "UPDATE tasks SET desc = ?, task = ?, priority = ? where task = ? AND date = ?"
        row = (new_desc, new_name, new_priority, curr_item, date,)
        cursor.execute(query, row)
        db.commit()

        # обновление задач в главном окне
        window.updateTasks(date)
        self.label.setText(new_name)

        messageBox = QMessageBox()
        messageBox.setWindowTitle("Saved")
        messageBox.setText("Changes saved.")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Новый экземпляр QApplication
    window = Window()
    window.show()  # Показываем окно
    window.act()
    app.exec()  # и запускаем приложение
