import os
import sys
import json
import glob
import time
import socket
import base64
import pyautogui
from des import *
from PyQt5 import QtCore, QtGui, QtWidgets


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
        self.server.bind(self.ip, self.port)
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


