import json
import select
from socket import socket, AF_INET, SOCK_STREAM, error
import pickle
import time
import datetime
import pickle

IP = 'localhost'


def wait_for_gamer(num_play, port=8888):
    reader = []
    writer = []
    errors = []
    player_index = {}
    i = 0
    with socket(AF_INET, SOCK_STREAM) as serverSocket:  # 創建socket
        serverSocket.bind((IP, port))  # bind to 127.0.0.1:8888
        print(f'Server waiting on {IP}:{port}')
        serverSocket.setblocking(0)  # NIO
        reader.append(serverSocket)
        serverSocket.listen(num_play+1)  # 監聽 num_play=最大監聽數量
        count_numofuser = 0
        while count_numofuser < num_play:
            readable, _, _ = select.select(reader, writer, errors)

            for s in readable:
                if s == serverSocket:
                    client, addr = serverSocket.accept()
                    client.setblocking(0)
                    player_index[f'{addr[0]}:{str(addr[1])}'] = i
                    i += 1
                    reader.append(client)
                    name, port = client.getpeername()
                    print(f'{name}:{port}', "is attend to the game")
                    count_numofuser += 1
                else:
                    try:
                        msg = s.recv(4096)
                        msg = json.loads(msg.decode('utf-8'))
                        if len(msg) is 0:
                            raise error
                        else:
                            sname, _ = s.getpeername()
                            print("get message from", sname)
                            print(msg)
                            # s.send(json.dumps(
                            #     "still wait for player").encode('utf-8'))
                    except:
                        reader.remove(s)
                        sname, _ = s.getpeername()
                        print("disconnect to ", sname)
                        s.close()
                        count_numofuser -= 1
    print("game start")
    reader = reader[1:]
    return serverSocket, reader, player_index
