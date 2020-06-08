import os
import subprocess
import sys
import random
import socket
import threading
from datetime import date
from pyDes import *
import time

def is_it_greeting(data):
    try:
        data = data.decode('utf-8')
        if data[-13::] == 'присоединился' or data[-15::] or data[-11::]:
            return 1
        else:
            return 0
    except: 
        return 0


def encrypted(messg):
    key = (date.today().strftime('%d%m%Y')).encode('utf-8')
    k = des(key, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    data = k.encrypt(messg)

    return data


def decrypted(messg):
    key = (date.today().strftime('%d%m%Y')).encode('utf-8')
    k = des(key, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    data = k.decrypt(messg, padmode=PAD_PKCS5)

    return data.decode('utf-8')


def making_check_phrase():
    final_phrase = ""
    for _ in range(17):
        num = random.randint(0, 9)
        final_phrase += str(num)
    
    return final_phrase


def account_check():   
    has_account = 0
    directory = os.getcwd()
    all_files = os.listdir(directory)
    for check_file in all_files:
        if check_file == ".info.mrbt":
            has_account = 1
    if has_account == 1:
        print("Аккаунт существует")
        file_data = open(".info.mrbt")
        raw_data = []
        for line in file_data:
            raw_data.append(line.strip())
    if has_account == 0:
        name = input("Your name: ")
        unic_str = making_check_phrase()
        raw_data = [name, unic_str]
        maked_file = open('.info.mrbt', 'w')
        for dat in raw_data:
            maked_file.write(dat)
            maked_file.write('\n')
        maked_file.close()

    return raw_data


def read_sok():
    while 1 :
        try:
            data = sock.recv(1024)
            if data.decode('utf-8') == 'u can quit':
                return False
            print(data.decode('utf-8'))
            check = is_it_greeting(data)
            if check == 1:
                if data.decode('utf-8') == "Такой пользователь уже существует!":
                    sock.close()
                    return False
                subprocess.call(["rm", ".info.mrbt"])
                if data.decode('utf-8') == "Нулевое имя не приветствуется!":
                    sock.close()
                    return False
        except:
            print(decrypted(data))


first_msg = 0
print("NetConnCat v1.0\nДля выхода напишите !quit\nWrite !quit for quitting\n")
server = ('192.168.1.8', 5052)
temp_data = account_check()
verify_phrase = str(temp_data[0]+":"+str(temp_data[1]))
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(('', 0))
sock.sendto((verify_phrase+' connected to server').encode('utf-8'), server)
listener = threading.Thread(target= read_sok)
listener.start()
stop_all = 0

while stop_all == 0:
    while 1:
        try:
            message = input()
            if message == '!quit':
                raise OSError
            if not message.strip():
                continue
            sock.sendto(encrypted((('['+verify_phrase.split(":")[0]+']')+message).encode('utf-8')), server)
        except (OSError, ValueError):
            sock.sendto(('quit please.').encode('utf-8'), server)
            print("Пока!")
            stop_all = 1
            break
