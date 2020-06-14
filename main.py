import NIOserver as server
import listen_control
import json
import Map

player_num = 2

socket, reader, player_index = server.wait_for_gamer(player_num)

for player in reader:
    if player is not socket:
        msg = [{'head': "game start"}]
        player.send((json.dumps(msg)).encode('utf-8'))
reader = reader[1:]
solidobject = [[0, 0]]
map = Map.Map(15, 13, 100, 100, player_num, solidobject)

listen_control.listen_control(socket, reader, map, player_index)
