import socket
import threading
import sys


class Send(threading.Thread):
	def __init__(self, sock, name):
		super().__init__()
		self.sock = sock
		self.name = name

	def run(self):
		while True:
			try:
				message = input(f"{self.name}: ")

				if message == 'quit':
					self.sock.sendall(
						f"[SERVER]: {self.name} has left".encode("utf-8"))
					break
				else:
					# send message for broadcasting
					msg = f"{self.name}: {message}".encode("utf-8")
					self.sock.sendall(msg)
			except KeyboardInterrupt:
				print("KeyBoardInterrupt..... exiting")
				sys.exit(0)
			except ConnectionAbortedError as err:
				print("Connection to the server was aborted\n", str(err))
				sys.exit(0)

		print("QUTTING....")
		self.sock.close()
		sys.exit(0)


class Receive(threading.Thread):
	def __init__(self, sock, name):
		super().__init__()
		self.sock = sock
		self.name = name

	def run(self):
		while True:
			try:
				message = self.sock.recv(2048)
				if message:
					print(f"\r{message.decode('utf-8')}\n{self.name}: ", end="")
				else:
					# server connection is closed
					# exit
					print("Hell, server connection is lost")
					print("QUITTING......")
					self.sock.close()
					sys.exit(0)
			except (ConnectionAbortedError, OSError):
				print()
				print("Connection to the server was aborted\n")
				sys.exit(0)



class Client:

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def start(self):
		print(f"Establishing connection to {self.host}:{self.port}")

		try:
			self.client_sock.connect((self.host, int(self.port)))
			print(
				f"Connection to {self.host}:{self.port}was establised successfully")
		except socket.error as err:
			print(f"Connection to {self.host}:{self.port} was unsuccessfully")

		print("\n")

		name = input("Enter nickname: ")

		print(f"What's good, {name}! You can now send the messages")

		# creating and starting the Send and Receive threads
		Send(self.client_sock, name).start()
		Receive(self.client_sock, name).start()

		self.client_sock.sendall(
			f"[SERVER]: {name} has joined the chat!".encode("utf-8"))
		print("\rYour are all set!!!!")
		print("Type 'quit' => To leave the chatroom anytime ")
		print(f"{name} => ", end='')


if __name__ == '__main__':
	host = '127.0.0.1'
	port = 3333
	client = Client(host, port)
	client.start()
