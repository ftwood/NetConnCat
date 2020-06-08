import socket
import json

def save_users(users_list):
	json.dump(users_list,open("users.txt","w"))


def load_users():
	temp = open("users.txt").read()
	upd_list = json.loads(temp)
	return upd_list


def make_verify(data, address):
	pass


def make_good_data(data):
	full_name = data[0:-20:1]
	pass_phrase = data[-37:-20:1]
	name = data[0:-38:1]
	return str(name), str(pass_phrase)


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(('192.168.1.8',5052))
client = []
users_list = {}

try:
	users_list = load_users()

except FileNotFoundError:
	print("Файла users.txt нет, по окончании создам")

print ('[✓]Server has been started')

try:
	while 1:
		data, address = sock.recvfrom(1024)
		try:
			if data.decode('utf-8') == 'quit please.':
				sock.sendto("u can quit".encode("utf-8"), address)
				continue
		except:
			pass

		if address not in client:
			try: 
				data.decode('utf-8')
				name, pass_phrase = make_good_data(data)
				
				if name in users_list and pass_phrase != users_list[name]:
					sock.sendto("Такой пользователь уже существует!".encode("utf-8"), address)
					continue
				
				if name == "b''":
					print("Нулевое имя у", str(address[0]))
					sock.sendto("Нулевое имя не приветствуется!".encode("utf-8"), address)
					continue

				else:
					client.append(address)
					users_list[str(name)] = str(pass_phrase)
					print(users_list)

				data = (name[2:-1:1] + ' присоединился').encode("utf-8")
				print(name[2:-1:1] + ' присоединился')

			except UnicodeDecodeError:
				continue

		for clients in client:
			if clients == address: 
				continue 
			sock.sendto(data,clients)

except KeyboardInterrupt:
	save_users(users_list)
