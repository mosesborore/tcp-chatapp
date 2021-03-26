import sys
import socket
import os
import threading


class Server(threading.Thread):

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.connections = []

    def run(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # SO_REUSEADDR option: allows the server to use the port after old
        # connection was closed
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            print("Binding...........")
            server_sock.bind((self.host, int(self.port)))
        except socket.error as err:
            print(f"Can't bind to the {self.host}: {self.port}")

        server_sock.listen(2)
        print(f"Server is listening at: {server_sock.getsockname()}")

        # accepting connections

        while True:
            client_conn, sock_address = server_sock.accept()
            print(
                f"[SERVER] new connection established with {sock_address}")

            # creating new thread
            server_socket = ServerSocket(client_conn, sock_address, self)

            # start the thread
            server_socket.start()

            # stores all active connections
            self.connections.append(server_socket)
            print("Ready to receive messages from: ",
                  client_conn.getpeername())

    def broadcast(self, src, msg):
        """
            broadcasts the message to other clients
            @param src: the source of the message
            @param msg: the message
        """
        for connection in self.connections:
            # sends to all clients except the source client
            if connection.sock_address != src:
                connection.send_message(msg)

    def remove_connection(self, server_socket):
        """ removes the closed connection from self.connections"""
        for conn in self.connections:
            if conn.sock_address == server_socket.sock_address:
                index = self.connections.index(conn)
                self.connections.pop(index)


class ServerSocket(threading.Thread):
    """
        manages and facilitates connection with each connected clients
    """

    def __init__(self, client_conn, sock_address, server):
        super().__init__()
        self.client_conn = client_conn
        self.sock_address = sock_address
        self.server = server  # Server object

    def run(self):

        # listening for the message sent by client(s)
        while True:
            # receive message from the client
            try:
                message = self.client_conn.recv(2048)
                if message:
                    print(f"{self.sock_address} says {message}")
                    # broadcast the message
                    self.server.broadcast(self.sock_address, message)
                else:
                    # client's socket connection is closed, exit the thread
                    print(f"{self.sock_address} connection is closed")
                    self.client_conn.close()
                    server.remove_connection(self)
                    return
            except ConnectionResetError as err:
                print("\nClient exited abruptly\n\n", str(err))
                self.client_conn.close()

    def send_message(self, message):
        """
                        sends all the message
        """
        self.client_conn.sendall(message)


def terminate_server(server):
    """ closes the server and all it connections """
    while True:
        command = input("")
        if command == 'out':
            print("Terminating all server connections....")
            for connection in server.connections:
                connection.client_conn.close()
            print("The server is shutting down.....")
            sys.exit(0)


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 3333

    server = Server(host, port)
    server.start()

    exit = threading.Thread(target=exit, args=(server,))
    exit.start()
