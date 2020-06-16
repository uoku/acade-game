import json
import sys
import NIOserver as server
import listen_control
import Map

##############################################
N_PLAYER = 2
MAP_ID = 1
POS = ((0, 0), (480, 480))
##############################################
port = 8888
if len(sys.argv) == 2:
    port = int(sys.argv[1])


def loadBlocks(p):
    l = []
    with open(p, 'r') as f:
        line = f.readline()
        while line:
            splited = line.split(',')
            x = int(splited[0])
            y = int(splited[1])
            status = int(splited[2])
            l.append([x, y, status])
            line = f.readline()
    return l

import random
solidobject = loadBlocks('blocks.txt')
for obj in solidobject:
    if obj[2] == 5:
        obj[2] = random.randint(1,3)
print(solidobject)
socket, reader, player_index = server.wait_for_gamer(N_PLAYER, port=port)
all_player_info = []
base_msg = {}
base_msg['map'] = {}
base_msg['map']['id'] = MAP_ID
base_msg['players'] = []
base_msg['solidobject'] = solidobject
for player, addr in zip(reader, player_index):
    idx = player_index[addr]
    info = {}
    info['id'] = idx
    info['x'] = POS[idx][1]
    info['y'] = POS[idx][0]
    info['status'] = 'ALIVE'
    base_msg['players'].append(info)

for player, idx in zip(reader, player_index):
    if player is not socket:
        msg = base_msg.copy()
        msg['control'] = player_index[idx]
        player.send((json.dumps(msg)).encode('utf-8'))
map = Map.Map(13, 13, 40, 40, N_PLAYER, solidobject)
map.set_client(reader)

listen_control.listen_control(socket, reader, map, player_index)
