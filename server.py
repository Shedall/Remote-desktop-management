import os
import sys
import json
import glob
import time
import socket
import base64
import pyautogui
#from des import *
from my_ui_file import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import distutils
#pyuic5 label.ui -o my_ui_file.py



class MyThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(list)
    def __init__(self, ip, port, parent=None):
        QtCore.QThread.__init__(self,parent)

        # Принимаем глобальные переменные
        self.active_socket = None
        self.ip = ip
        self.port = port
        self.command = 'screen'

        # Создаем TCP-Сервер
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.port))
        self.server.listen(0)


    #Принимаем и обрабатываем изображения
    def run(self):
        #Принимаем входящее соеденение
        self.data_connection, _ = self.server.accept()
        self.active_socket = self.data_connection

        while True:
            if self.command.split(' ')[0] != 'screen':
                self.send_json(self.command.split(' '))
                response = self.receive_json()
                self.mysignal.emit([response])
                self.command = 'screen'
            if self.command.split(' ')[0] == 'screen':
                self.send_json(self.command.split(' '))
                response = self.receive_json()
                self.mysignal.emit([response])



    #Отправка JSON-данных клиенту
    def send_json(self,data):
        #Обрабатываем бинарные данные
        try:json_data = json.dumps(data.decode('utf-8'))
        except:json_data = json.dumps(data)

        #Случай если клиент разорвал соеденение но сервер отправляет команды
        try:
            self.active_socket.send(json_data.encode('utf-8'))
        except ConnectionResetError:
            #Отключаемся от текущей сессии
            self.active_socket = None


    #Получаем JSON-данные от клиента
    def receive_json(self):
        json_data = ''

        while True:
            try:
                if self.active_socket != None:
                    json_data += self.active_socket.recv(1024).decode('utf-8')
                    return json.loads(json_data)
                else:
                    return None
            except ValueError:
                pass


class VNCServer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #self.ui.label.setText("Привет, мир!")

        #Создаем экземпляр обрабочтчика
        self.ip = '192.168.221.134'
        #self.ip = '127.0.0.1'
        self.port = 4444
        self.thread_handler = MyThread(self.ip,self.port)
        self.thread_handler.start()

        #Обработчик потока для обновления GUI
        self.thread_handler.mysignal.connect(self.screen_handler)


        #Обработка и вывод изображений
    def screen_handler(self, screen_value):
        data = ['mouse_left_click','mouse_right_click','mouse_double_left_click']

        #В случае если не скрин-пропускаем шаг
        if screen_value[0] not in data:
            decrypt_image = base64.b64decode(screen_value[0])
            with open('2.png', 'wb') as file:
                file.write(decrypt_image)

            #Выводим изображение в панель
            image = QtGui.QPixmap('2.png')
            self.ui.label.setPixmap(image)

    #После закрытия сервера удаляем изщображение
    def closeEvent(self, event):
        for file in glob('*.png'):
            try: os.remove(file)
            except: pass


    #Обработка event события
    def event(self, event):
        # обработкаЛКМ ПКМ
        if event.type() == QtCore.QEvent.MouseButtonPress:
            current_button = event.button() #Определяем нажатую кнопку

            if current_button == 1:
                mouse_cord = f'mouse_left_click {event.x()} {event.y()}'
            elif current_button == 2:
                mouse_cord = f'mouse_right_click {event.x()} {event.y()}'
            self.thread_handler.command = mouse_cord

        #Обработка double-кликов
        elif event.type() == QtCore.QEvent.MouseButtonDblClick:
            mouse_cord = f'mouse_double_left_click {event.x()} {event.y()}'
            self.thread_handler.command = mouse_cord
        return QtWidgets.QWidget.event(self, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = VNCServer()
    myapp.show()
    sys.exit(app.exec_())
