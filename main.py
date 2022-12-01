import sys
import time
import random
import sqlite3
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from yproject2 import Ui_MainWindow


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        QtWidgets.QMessageBox.about(self,
                                    'Оповещение', 'Для начала тестирования кликните левой кнопкой мыши вне сроки ввода')
        self.time_start = 0
        self.total_time = 0
        self.input_text = ''
        self.accuracy = 0
        self.wpm = 0
        self.word = ''
        self.best_wpm = 0
        self.best_accuracy = 0
        self.word = self.get_sentence()
        self.setWindowIcon(QtGui.QIcon('keyboard.png'))
        self.btn_re.setIcon(QtGui.QIcon('icon (1) (1).png'))
        self.btn_re.setIconSize(QtCore.QSize(200, 240))
        self.btn_re.clicked.connect(self.reset_game)
        self.lbl_out.setText(self.word)
        self.label_2.setText(f'Time: {self.total_time}')
        self.label_3.setText(f'Wpm: {self.wpm}')
        self.label_4.setText(f'Accuracy: {self.accuracy}%')
        self.sign_in.clicked.connect(self.login)
        self.sign_up.clicked.connect(self.reg)

    def event(self, e):
        """
        Функция, которая обрабатывает нажатие левой кнопки мыши для включения таймера и нажатие ENTER для
        выключения таймера
        """
        if e.type() == QtCore.QEvent.KeyPress:
            if e.key() == 16777220:
                self.total_time = time.time() - self.time_start
                self.input_text = self.line_in.text()
                self.show_res()
        elif e.type() == QtCore.QEvent.MouseButtonPress:
            self.time_start = time.time()
        return QMainWindow.event(self, e)

    def get_sentence(self):
        """
        Функция, которая достаёт из текстового файла случайное предложение
        """
        f = open('text.txt').read()
        sentences = f.split('\n')
        sentence = random.choice(sentences)
        return sentence

    def show_res(self):
        """
        В этой функции сравнивается по каждому символу строка из переменной self.word и введённая строка, затем
        считаются и выводятся пользователю значения time, wpm, accuracy
        """
        cnt = 0
        for i, c in enumerate(self.word):
            try:
                if self.input_text[i] == c:
                    cnt += 1
            except Exception:
                pass
        self.accuracy = cnt / len(self.word) * 100
        self.wpm = (len(self.input_text) / 5) / (self.total_time / 60)
        self.label_2.setText(f'Time: {int(self.total_time)}s')
        self.label_3.setText(f'Wpm: {round(self.wpm, 1)}')
        self.label_4.setText(f'Accuracy: {round(self.accuracy, 1)}%')
        self.best()

    def reset_game(self):
        """
        В этой функции значения всех переменных сбрасываются до исходных
        """
        self.word = self.get_sentence()
        self.lbl_out.setText(self.word)
        self.line_in.clear()
        self.input_text = ''
        self.time_start = 0
        self.total_time = 0
        self.accuracy = 0
        self.wpm = 0
        self.label_2.setText(f'Time: {self.total_time}')
        self.label_3.setText(f'Wpm: {self.wpm}')
        self.label_4.setText(f'Accuracy: {self.accuracy}%')

    def best(self):
        """
        Здесь происходит подключение к БД, создание курсора, измениение значений переменых best_wpm, best accuracy,
        изменение этих значений в таблице БД
        """
        self.user_login = self.log.text()
        self.user_password = self.pswrd.text()
        self.db = sqlite3.connect('data.db')
        self.sql = self.db.cursor()
        self.sql.execute(f"""SELECT wpm, accuracy 
                          FROM users WHERE (login = '{self.user_login}') 
                          AND (password = '{self.user_password}')""")
        self.res = self.sql.fetchone()
        self.best_wpm = self.res[0]
        self.best_accuracy = self.res[1]
        if self.wpm > self.best_wpm:
            self.best_wpm = round(self.wpm, 1)
        if self.accuracy > self.best_accuracy:
            self.best_accuracy = round(self.accuracy, 1)
        self.sql.execute(f"""UPDATE users 
                         SET wpm = '{self.best_wpm}' 
                         WHERE login = '{self.user_login}'""")
        self.db.commit()
        self.sql.execute(f"""UPDATE users 
                         SET accuracy = '{self.best_accuracy}' 
                         WHERE login = '{self.user_login}'""")
        self.db.commit()

    def login(self):
        """
            Здесь происходит подключение к БД, создание курсора, вход в аккаунт пользователя по введённому логину и
            паролю, вывод оповещения и текущих значений best_wpm и best_accuracy.
        """
        self.user_login = self.log.text()
        self.user_password = self.pswrd.text()
        self.db = sqlite3.connect('data.db')
        self.sql = self.db.cursor()
        try:
            self.sql.execute(f"""SELECT login, password 
                             FROM users WHERE login = '{self.user_login}'""")
        except Exception:
            pass
        self.db.commit()
        self.value = self.sql.fetchall()
        if len(self.value) == 0:
            QtWidgets.QMessageBox.about(self, 'Оповещение', 'Такой пользователь не зарегистрирован')
        elif len(self.value) != 0 and self.value[0][1] == self.user_password:
            self.sql.execute(f"""SELECT wpm, accuracy 
                                      FROM users WHERE (login = '{self.user_login}') 
                                      AND (password = '{self.user_password}')""")
            self.b_res = self.sql.fetchone()
            self.best_wpm = self.b_res[0]
            self.best_accuracy = self.b_res[1]
            QtWidgets.QMessageBox.about(self, 'Оповещение', f'Вы успешно вошли в систему\nBest wpm: {self.best_wpm}\n'
                                                            f'Best accuracy: {self.best_accuracy}%')
            self.best()
        else:
            QtWidgets.QMessageBox.about(self, 'Оповещение', 'Такой пользователь не зарегистрирован')

    def reg(self):
        """
            Здесь происходит подключение к БД, создание курсора, проверка корректности введённых данных, регистрация
            пользователя по введённому логину и паролю, добавление новых данных в таблицу БД, вывод оповещения
        """
        self.user_login = self.log.text()
        self.user_password = self.pswrd.text()
        self.db = sqlite3.connect('data.db')
        self.sql = self.db.cursor()

        if len(self.user_login) > 1 and len(self.user_password) > 1:
            try:
                self.sql.execute(f"""SELECT login, password FROM users WHERE login = '{self.user_login}'""")
            except Exception:
                pass
            if not self.sql.fetchone():
                self.sql.execute(f"""INSERT INTO users 
                                 VALUES (?, ?, ?, ?)""", (self.user_login, self.user_password,
                                                                                0, 0))
                self.db.commit()
                QtWidgets.QMessageBox.about(self, 'Оповещение', 'Вы успешно зарегистрированы')

            else:
                QtWidgets.QMessageBox.about(self, 'Оповещение', 'Такой пользователь уже зарегистрирован')
        elif len(self.user_login) < 2 or len(self.user_password) < 2:
            QtWidgets.QMessageBox.about(self, 'Оповещение', 'Длина вводимых данных должна превышать 1 символ')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
