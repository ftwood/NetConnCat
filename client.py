import os
import subprocess
import sys
import random
import socket
import threading
from datetime import date
from pyDes import *
import time
import rsa
import string


def secret_chat_listener():
    print("Начинаю обмен ключами")
    (pubkey, privkey) = rsa.newkeys(512)  #генерация пары ключей                                        // generating a pair of keys
    sock.sendto(str(pubkey).encode('utf-8'),
                server)  #отправка открытого ключа партнеру                                             // sending pubkey to companion
    while True:
        try:
            data = sock.recv(1024)
            if len(data.decode('utf-8')) == 172:
                pubkey = data.decode('utf-8')  #получаем ключ собеседника                               // getting companion's pubkey
                pubkey = rsa.key.PublicKey(
                    int(pubkey[10:-8]), int(pubkey[-6:-1])
                )  #преобразовываем строку в класс rsa.key.PublicKey для успешной шифровки сообщений    // converting string to class rsa.key.PublicKey for successful decryption
                break
        except:
            pass
    secret_sender = threading.Thread(
        target=secret_chat_sender, args=[pubkey]
    )  #поток отправления сообщений в аргументы принимает публичный ключ пользователя                   // sender threading takes companion's pubkey as an argument
    secret_sender.start()
    time.sleep(0.1)
    print("Запуск секретного чата")
    while True:
        try:
            data = sock.recv(1024)
            if data.decode('utf-8') == 'u can quit':
                return False
        except:
            try:
                messg = rsa.decrypt(data, privkey)  #расшифровка сообщения                               // decrypting message
                print(messg.decode('utf-8'))
            except:
                print("Проблема с ключом")
                continue


def secret_chat_sender(pbkey):
    time.sleep(3)
    subprocess.call("clear")
    print(
        "Вы в секретном чате. Чтобы начать переписку, напишите !start. Удачи.")
    while True:
        message = input()
        if message == '!quit':
            sock.sendto(('quit please.').encode('utf-8'), server)
            return 0
        if not message.strip():
            continue
        crypted = rsa.encrypt(message.encode('utf-8'),
                              pbkey)  #шифрование сообщения ключом собеседника                            // encrypting message by companion's pubkey
        sock.sendto(crypted, server)


#запрос на получение списка пользователей                                                                 // request to get a list of users
def send_me_users():
    sock.sendto(('sendmeusers...').encode('utf-8'), server)


#запрос на секретный чат                                                                                  // secret chat request 
def make_chat():
    user = input("Секретный чат с ")
    sock.sendto(("talkwith{0}".format(user)).encode("utf-8"), server)


#вступил ли кто-то в беседу?                                                                              // Has anyone entered the conversation?
def is_it_greeting(data):
    try:
        data = data.decode('utf-8')
        if data[-13::] == 'присоединился' or data[-15::] or data[-11::]:
            return 1
        else:
            return 0
    except:
        return 0


#шифрование сообщения                                                                                     // encrypting message(DES)
def encrypted(messg):
    key = (date.today().strftime('%d%m%Y')).encode(
        'utf-8')  #пусть наш ключ будет сегодняшней датой                                                 // let our key be today's date
    k = des(key, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    data = k.encrypt(messg)

    return data


#дешифрование сообщения                                                                                   // decrypting message(DES)
def decrypted(messg):
    key = (date.today().strftime('%d%m%Y')).encode(
        'utf-8')  #пусть наш ключ будет сегодняшней датой                                                 // let our key be today's date
    k = des(key, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    data = k.decrypt(messg, padmode=PAD_PKCS5)

    return data.decode('utf-8')


#создание уникального id                                                                                  // creating unic_id
def making_id():
    final_id = ""
    for _ in range(17):
        num = random.randint(0, 9)
        final_id += str(num)

    return final_id


#проверка наличия аккаунта и его создание при отсуствии .info.mrbt                                        // checking for an account and creating it in the absence of a file .info.mrbt
#в .info.mrbt содержатся данные пользователя                                                              // .info.mrbt stores user data
def account_check():
    has_account = 0
    all_files = os.listdir(
        os.getcwd())  #получение списка файлов в текущей директории                                       // getting a list of files in the current directory 
    for check_file in all_files:
        if check_file == ".info.mrbt":
            has_account = 1
    if has_account == 1:
        print("Аккаунт существует")
        file_data = open(".info.mrbt")
        raw_data = []
        for line in file_data:
            raw_data.append(line)  #считываем данные из .info.mrbt в raw_data                             // creating raw_data from .info.mrbt
        print("Ваше имя - {}".format(raw_data[0].split()[0]))
        return raw_data[0].split()
    if has_account == 0:
        name = ''
        while not name.strip():  #пока имя представляет собой ''                                          // while name=''
            name = input("Your name: ")
            name_char = list(name)
            for char in name_char:
                if char not in string.ascii_letters:
                    print("Имя должно состоять из латинских букв")
                    name = ''
                    break
        unic_id = making_id()
        raw_data = [name, unic_id]
        maked_file = open('.info.mrbt', 'w')
        for dat in raw_data:  #запись данных в файл                                                       // writing data to the file
            maked_file.write(dat)
            maked_file.write(' ')
    return raw_data


def read_sock():
    while 1:
        try:
            data = sock.recv(1024)
            if data.decode('utf-8')[0:21] == "С вами хочет вступить":
                print(data.decode('utf-8'))
                user_who_send = data.decode('utf-8')[
                    38:]  #получение имени собеседника                                                    // getting companion's name
                choose = ''
                while True:
                    choose = input("Принять предложение?  yes/no ")
                    if choose == "yes" or choose == "no":
                        break
                    else:
                        choose = ''
                sock.sendto((choose + user_who_send).encode('utf-8'), server)
                if choose == "yes":
                    secret_listener.start()
                    return False
                continue

            if data.decode('utf-8') == "Чат одобрен":
                print(data.decode('utf-8'))
                secret_listener.start()
                return False

            if data.decode('utf-8') == 'u can quit':
                return False
            print(data.decode('utf-8'))
            check = is_it_greeting(data)
            if check == 1:
                if data.decode(
                        'utf-8') == "Такой пользователь уже существует!":
                    subprocess.call(["rm", ".info.mrbt"])
                    account_check()
                    sock.close()
                    print("Имя создано, напишите !stop")
                    return False
        except:
            print(decrypted(data))


first_msg = 0
print()
print("""| \ | |    | |  / ____|                 / ____|    | |  
|  \| | ___| |_| |     ___  _ __  _ __ | |     __ _| |_ 
| . ` |/ _ \ __| |    / _ \| '_ \| '_ \| |    / _` | __|
| |\  |  __/ |_| |___| (_) | | | | | | | |___| (_| | |_ 
|_| \_|\___|\__|\_____\___/|_| |_|_| |_|\_____\__,_|\__|""")
print(
    "\nДля выхода напишите !quit\nДля отображения списка пользователей напишите !users\nДля входа в секретный чат напишите !secret\nДля смены имени пользователя !changename\n"
)
server = ('127.0.0.1', 8848)
temp_data = account_check()
verify_phrase = str(temp_data[0] + ":" + str(temp_data[1]))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 0))
sock.sendto((verify_phrase + ' connected to server').encode('utf-8'), server)
listener = threading.Thread(target=read_sock)  #основной поток сообщений                                // main thread
secret_listener = threading.Thread(
    target=secret_chat_listener)  #секретный поток сообщений                                            // secret chat thread

listener.start()
stop_all = 0

while stop_all == 0:
    while 1:
        try:
            message = input()
            if message == "!start":
                stop_all = 1
                break
            if message == '!secret':
                make_chat()
                continue
            if message == "!stop":
                stop_all = 1
                break
            if message == '!quit':
                sock.sendto(('quit please.').encode('utf-8'), server)
                stop_all = 1
                break
            if message == '!users':
                print("Список участников: \n")
                send_me_users()
            if message == '!changename':
                sock.sendto(('!changename').encode('utf-8'), server)
                subprocess.call(["rm", ".info.mrbt"])
                new_name = account_check()[0]
                sock.sendto(
                    encrypted(
                        (verify_phrase.split(":")[0] +
                         " меняет имя на {}".format(new_name)).encode('utf-8')
                    ),  #уведомление пользователей о смене имени                                        // notifying users about name change    
                    server)
                print("Имя изменено, запустите client.py еще раз")
                stop_all = 1
                break
            if not message.strip():  #если сообщение пустое                                             // if message is empty
                continue
            sock.sendto(
                encrypted((('[' + verify_phrase.split(":")[0] + ']') +
                           message).encode('utf-8')), server)
        except:
            pass
