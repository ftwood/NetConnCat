import socket
import json
import threading
import time


#выгрузка пользователей в users.txt                                     // loading users into users.txt
def save_users(users_list):
    json.dump(users_list, open("users.txt", "w"))


#получение списка пользователей из users.txt                            // getting a list of users from users.txt
def load_users():
    temp = open("users.txt").read()
    upd_list = json.loads(temp)
    return upd_list


#получение имени и уникального идентификатора из сообщения пользователя // getting the name and id from the user's letter
def make_good_data(data):
    user_id = data[-37:-20:1]
    name = data[0:-38:1]
    return str(name), str(user_id)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 8848))
clients = []  #пользовательские ip                                      // users ip
users_list = {} #словарь name:user_id                                   // dict name:user_id
users_list_to_post = {} #словарь name:ip                                // dict name:ip 
secret_users = {} #связки пользователей в секретных чатах               // pairs of users in secure chats
temp_secret_users = {} #временные секретные связки                      // temporary pairs of users
change_name_users = {} #пользователи, меняющие имя                      // users changing name

try:
    users_list = load_users()
except FileNotFoundError:
    print("Файла users.txt нет, по окончании создам")

print('[✓]Server has been started')

try:
    while 1:
        data, address = sock.recvfrom(1024)
        try:
            #узнаем имя отправившего сообщение пользователя              // find out the name of the user who sent the message
            for name, adr in users_list_to_post.items():
                if adr == address:
                    user_who_send = name

            if user_who_send in secret_users.keys():
                try:
                    if data.decode('utf-8') == 'quit please.':
                        sock.sendto("u can quit".encode("utf-8"), address)
                        secret_users.pop(user_who_send)
                        continue
                except:
                    sock.sendto(
                        data, users_list_to_post[secret_users[user_who_send]])
                    time.sleep(0.8)
                    continue

            elif user_who_send in secret_users.values():
                for usr_to_talk, usr_who_send in secret_users.items():
                    if usr_who_send == user_who_send:
                        user_to_talk = usr_to_talk
                try:
                    if data.decode('utf-8') == 'quit please.':
                        sock.sendto("u can quit".encode("utf-8"), address)
                        secret_users.pop(user_to_talk)
                except:
                    sock.sendto(data, users_list_to_post[user_to_talk])
                    time.sleep(0.8)
                    continue
            if data.decode('utf-8') == '!changename':
                users_list_to_post.pop(
                        user_who_send)  #удаление прошлой связки имя:user_id // deleting a last pair name:user_id
                sock.sendto("u can quit".encode("utf-8"), address)
                continue
            if data.decode('utf-8') == 'quit please.':
                sock.sendto("u can quit".encode("utf-8"), address)
                continue

            if data.decode('utf-8')[
                    0:8] == "talkwith": #отправка приглашения в секретный чат // sending an invitation to a secret chat
                user_to_talk = data.decode('utf-8')[8:]
                for name, adr in users_list_to_post.items():
                    if adr == address:
                        user_who_send = name
                try:
                    sock.sendto(
                        "С вами хочет вступить в секретный чат {0}".format(
                            user_who_send).encode('utf-8'),
                        users_list_to_post[user_to_talk])
                except:
                    sock.sendto("Неверно введено имя пользователя!", address)
                temp_secret_users[
                    user_to_talk] = user_who_send #установление временной связки // establishing a temporary pair
                continue
            elif data.decode(
                    'utf-8'
            ) == 'sendmeusers...':  #отправляем список пользователей             // sending users_list_to_post
                for name, adress in users_list_to_post.items():
                    if name == user_who_send:
                        sock.sendto((name + " - вы").encode('utf-8'), address)
                    else:
                        sock.sendto(name.encode('utf-8'), address)
                continue
            elif data.decode('utf-8')[0:3] == 'yes':  #если запрос принят        // if the request is accepted
                user_to_talk = data.decode('utf-8')[3:]
                for name, adr in users_list_to_post.items():
                    if adr == address:
                        user_who_send = name
                secret_users[
                    user_who_send] = user_to_talk  #связываем пользователей      // connecting users
                sock.sendto("Чат одобрен".encode("utf-8"),
                            users_list_to_post[user_to_talk])
            elif data.decode('utf-8')[0:2] == 'no':  #если запрос отклонен       // if the request is canceled
                user_to_talk = data.decode('utf-8')[2:]
                for name, adr in users_list_to_post.items():
                    if adr == address:
                        user_who_send = name
                temp_secret_users.pop(
                    user_who_send)  # удаляем временную связку пользователей     // deleting a temporary pair
                continue
        except:
            pass

        if address not in clients:
            try:
                name, user_id = make_good_data(data)
                if name in users_list and user_id != users_list[name]:
                    sock.sendto(
                        "Такой пользователь уже существует!".encode("utf-8"),
                        address)
                    continue

                else:
                    clients.append(address)
                    users_list[str(name)] = str(user_id)
                    users_list_to_post[str(name[2:-1:1])] = address

                data = (name[2:-1:1] + ' присоединился').encode("utf-8")
                print(name[2:-1:1] + ' присоединился')

            except UnicodeDecodeError:
                continue

        for client in clients:
            if client == address:
                continue  #не отправляем сообщение клиента ему же                // do not send a client message to himself
            sock.sendto(data, client)

except KeyboardInterrupt:
    save_users(users_list)
