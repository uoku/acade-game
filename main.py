import NIOserver as server
import listen_control
import json
import Map

##############################################
N_PLAYER = 2
MAP_ID = 0
P0_POS = (0, 0)
P1_POS = (120, 120)
##############################################

socket, reader, player_index = server.wait_for_gamer(N_PLAYER)
all_player_info = []
base_msg = {}
base_msg['map'] = {}
base_msg['map']['id'] = 1
base_msg['players'] = []
for player, idx in zip(reader, player_index):
    info = {}
    info['id'] = idx
    info['x'] = P0_POS[1] if idx == 0 else P1_POS[1]
    info['y'] = P0_POS[0] if idx == 0 else P1_POS[0]
    info['status'] = 'ALIVE'
    base_msg['players'].append(info)

for player, idx in zip(reader, player_index):
    if player is not socket:
        msg = base_msg.copy()
        msg['map'] = {}
        msg['map']['id'] = 1
        msg['players'] = []
        for player, idx in zip(reader, player_index):

        msg = [{'head': "game start"}]
        player.send((json.dumps(msg)).encode('utf-8'))
solidobject = [[0, 0]]
map = Map.Map(15, 13, , 100, N_PLAYER, solidobject)

listen_control.listen_control(socket, reader, map, player_index)
