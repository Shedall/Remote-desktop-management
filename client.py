import socket
#192.168.50.157


class ClientApp:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(
            ('192.168.50.157', 5555))  # Замените 'ip_address_of_server' на IP-адрес сервера

        self.run_client()

    def run_client(self):
        while True:
            command = input("Enter command (e.g., 'move_up', 'click', etc.): ")
            if command == "exit":
                break
            self.send_command(command)

    def send_command(self, command):
        self.client_socket.sendall(command.encode())


# Запускаем клиент
client_app = ClientApp()
