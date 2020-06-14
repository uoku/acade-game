import json
import select
from socket import socket, AF_INET, SOCK_STREAM, error
import pickle, time, datetime
import pickle

PORT = 8888
def wait_for_gamer(num_play):
    reader = []
    writer = []
    errors = []
    player_index = {}
    i = 0
    with socket(AF_INET, SOCK_STREAM) as serverSocket:  # 創建socket
        serverSocket.bind(("127.0.0.1", PORT))  # bind to 127.0.0.1:8888
        serverSocket.setblocking(0)  # NIO
        reader.append(serverSocket)
        serverSocket.listen(num_play+1)  # 監聽 num_play=最大監聽數量
        count_numofuser = 0
        while count_numofuser < num_play:
            readable, writable, exceptions = select.select(reader, writer, errors)

            for s in readable:
                if s == serverSocket:
                    client, address = serverSocket.accept()
                    client.setblocking(0)
                    player_index[str(address[1])]=i
                    i += 1
                    reader.append(client)
                    name, port = client.getpeername()
                    print(name, "is attend to the game")
                    count_numofuser += 1
                else:
                    try:
                        message = s.recv(10000)
                        message = json.loads(message.decode('utf-8'))
                        if len(message) is 0:
                            raise error
                        else:
                            sname, sport = s.getpeername()
                            print("get message from", sname)
                            s.send(json.dumps("still wait for player").encode('utf-8'))
                    except:
                        reader.remove(s)
                        sname, sport = s.getpeername()
                        print("disconnect to ", sname)
                        s.close()
                        count_numofuser -= 1
    print("game start")
    reader = reader[1:]
    return serverSocket, reader, player_index


