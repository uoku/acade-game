import json
import select
from socket import error
from threading import Timer


def listen_control(socket, reader, map, player_index):
    while True:
        readable, writable, exceptional = select.select(reader, [], [])

        for s in readable:
            if s is not socket:
                message = s.recv(4096)
                message = json.loads(message.decode('utf-8'))
                print(f'Server receives {json.dumps(message, indent=4)}')
                name, port = s.getpeername()
                playername = player_index[f'{name}:{str(port)}']
                if f'player{playername}' not in message:
                    continue
                # 處理json message
                action = message[f'player{playername}']
                # end
                if (map.player[playername][5] is 3) or (map.player[playername][5] is 4):
                    donothing = True
                # 放開的時候 回傳 
                # right
                elif action == 10:
                    map.press_up(playername, 10)
                # down
                elif action == 20:
                    map.press_up(playername, 20)                
                # left
                elif action == 30:
                    map.press_up(playername, 30)
                # up
                elif action == 40:
                    map.press_up(playername, 40)
                # 根據 收到的json 做移動跟放水球
                elif action is 0:
                    # move up
                    move = 0
                    map.change_direction(playername, move)
                    map.change_player_position(playername, move)
                elif action is 1:
                    # move right
                    move = 1
                    map.change_direction(playername, move)
                    map.change_player_position(playername, move)
                elif action is 2:
                    # move down
                    move = 2
                    map.change_direction(playername, move)
                    map.change_player_position(playername, move)
                elif action is 3:
                    # move left
                    move = 3
                    map.change_direction(playername, move)
                    map.change_player_position(playername, move)
                elif action is 4:
                    # set waterball
                    move = 4
                    x, y = map.set_waterball(playername)

                    # 設定timer 等待爆炸
                    def waterball_bomb(player_num, x, y):
                        print(x, y, player_num)
                        map.bomb(player_num, x, y)
                        # send map info
                        reply = map.get_change()
                        # end
                        for client in reader:
                            client.send(json.dumps(reply).encode('utf-8'))

                        # 設定水柱結束
                        def end_bomb():
                            map.end_bomb(x, y)
                            # send map info
                            reply = map.get_change()
                            # end
                            for client in reader:
                                client.send(json.dumps(reply).encode('utf-8'))

                        tt = Timer(0.5, end_bomb)
                        tt.start()

                    if x is not None and y is not None:
                        t = Timer(2.0, waterball_bomb, [playername, x, y])
                        t.start()
                else:
                    # errors
                    print('something wrong')
                    # end
                # 從map 物件 拿出更改的資訊 存成json
                reply = map.get_change()
                #
                for client in reader:
                    if client is not socket:
                        client.send(json.dumps(reply).encode('utf-8'))
