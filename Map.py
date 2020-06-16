import math
import copy
from threading import Timer
import json


# water ball 還沒加到solid obj

def colision(p1, p2):  # p[x , y ,w ,h]
    minx1 = p1[0] - p1[2] / 2
    maxx1 = p1[0] + p1[2] / 2
    miny1 = p1[1] - p1[3] / 2
    maxy1 = p1[1] + p1[3] / 2

    minx2 = p2[0] - p2[2] / 2
    maxx2 = p2[0] + p2[2] / 2
    miny2 = p2[1] - p2[3] / 2
    maxy2 = p2[1] + p2[3] / 2
    if (maxx1 > minx2 and maxx2 > minx1 and maxy1 > miny2 and maxy2 > miny1):
        return True
    else:
        return False


# solidobj [x ,y ,種類] 0:固體 1:鞋子 2:+水球數 3:+威力 4:水球(會爆炸的) 5:Breakable


class Map():
    def __init__(self, x, y, w, h, playernum, solidobj):  # w,h is cell   x,y is 有幾格
        self.eatobj_size = [100, 100]  # 鞋子 水球 ... 的 大小
        self.all_change = []  # 用來存 變化的狀態
        self.timedis = 1  # 移動距離
        self.cell = [w, h]  # 地圖方格大小
        self.map = [x * w, y * h]  # 地圖像素大小
        self.cellmap = [x, y]  # 地圖方格
        self.solidobj = solidobj  # 固體 [包含吃的東西]
        self.cell_solidobj = []  # 用於水球爆炸判斷
        for obj in self.solidobj:
            self.cell_solidobj.append([obj[0] // w, obj[1] // w])
        # end
        self.waterball = []
        self.init_speed = 5
        self.init_waterball = 2
        self.init_power = 2
        self.size = [30, 30]
        self.status = 0
        self.player = []
        play_pos = [[0, 0], [560, 480]]
        for i in range(playernum):
            position = play_pos[i]
            direciotn = 1
            player_list = [self.init_speed, self.init_waterball, self.init_power, position, self.size, self.status,
                           direciotn]
            self.player.append(player_list)

    def set_client(self, client):
        self.client = client

    def add_player_speed(self, player_num):
        self.player[player_num][0] += 1

    def add_player_waterball(self, player_num):
        self.player[player_num][1] += 1

    def add_player_power(self, player_num):
        self.player[player_num][2] += 1

    def change_player_position(self, player_num, direct):
        # need to 判斷碰撞
        move_dis = self.player[player_num][0] * self.timedis
        x, y = self.player[player_num][3]
        new_x, new_y = x, y
        if direct is 0:
            new_y = y - move_dis
        elif direct is 1:
            new_x = x + move_dis
        elif direct is 2:
            new_y = y + move_dis
        elif direct is 3:
            new_x = x - move_dis
        else:
            raise ValueError('move error')
        for obj in self.solidobj:
            if colision([new_x, new_y, self.size[0], self.size[1]], [obj[0], obj[1], self.cell[0], self.cell[1]]) and (
                    obj[2] == 0):
                new_x, new_y = x, y
        # 邊界判斷
        if new_x < 0:
            new_x = 0
        if new_x > self.map[0]:
            new_x = self.map[0] - self.size[0]
        if new_y < 0:
            new_y = 0
        if new_y > self.map[1]:
            new_y = self.map[1] - self.size[1]
        # end
        # 撞死人判斷
        for idx, player in enumerate(self.player):
            if (player is not self.player[player_num]) and (player[5] is 3):
                if colision([player[3][0], player[3][1], player[4][0], player[4][1]],
                            [self.player[player_num][3][0], self.player[player_num][3][1],
                             self.player[player_num][4][0], self.player[player_num][4][1]]):
                    player[5] = 4
                    self.all_change.append({
                        'header': 'player_dead',
                        'idx': idx,
                        'position': player[3]
                    })

        # 吃東西判斷
        if new_x != x and new_y != y:
            for object in self.solidobj:
                pos = [math.ceil((new_x + self.player[player_num][4][0] // 2) // self.cell[0]),
                       math.ceil((new_y + self.player[player_num][4][1]) // self.cell[1])]
                if (pos[0] == object[0]//self.cell[0]) and (pos[1] == object[1]//self.cell[1]):
                    # object[2] 是 物品種類
                    if object[2] == 1:  # 鞋子
                        self.add_player_speed(player_num)
                        ##
                        # self.player[player_num][0] += 1
                    elif object[2] == 2:  # 水球
                        self.add_player_waterball(player_num)
                        # self.player[player_num][1] += 1
                    elif object[2] == 3:  # 威力
                        self.add_player_power(player_num)
                        # self.player[player_num][2] += 1
                    else:
                        raise ValueError('eat error')
                    self.all_change.append({
                        'header': 'player_ability',
                        'idx': player_num,
                        'position': [object[0], object[1]]
                    })

        # 改 self.player 的 position
        self.player[player_num][3] = [new_x, new_y]
        # 加到 all change
        self.all_change.append({
            'header': 'player',
            'idx': player_num,
            'position': [new_x, new_y]
        })

    # 放開時回傳
    def press_up(self, playernum, direction):
        self.all_change.append({
            'header': 'press_up',
            'idx': playernum,
            'direction': direction
        })

    def change_status(self, player_num, status):
        self.player[player_num][5] = status

    def set_waterball(self, player_num):
        if self.player[player_num][1] is not 0:
            x, y = self.player[player_num][3]
            a, b = [math.ceil((x + self.player[player_num][4][0] // 2) // self.cell[0]),
                    math.ceil((y + self.player[player_num][4][1] // 2) // self.cell[0])]
            self.waterball.append([a, b])
            self.player[player_num][1] -= 1
            # 加到all change
            self.all_change.append({
                'header': 'add_ball',
                'position': [a, b]
            })
            #
            return a, b
        else:
            return None, None

    def bomb(self, player_num, x, y):
        self.player[player_num][1] += 1
        power = self.player[player_num][2]
        #  water_pos = [left forword right back]
        water_pos = self.get_max_pos(x, y, power)
        # 炸成泡判斷
        buble_player_pos = []
        buble_player_idx = []
        for idx, player in enumerate(self.player):
            pos = player[3]
            pos = [math.ceil((pos[0] + player[4][0] // 2) // self.cell[0]),
                   math.ceil((pos[1] + player[4][1]) // self.cell[1])]
            if (water_pos[0][0] <= pos[0] <= water_pos[2][0] and pos[1] == water_pos[0][1]) or \
                    (water_pos[1][0] == pos[0] and water_pos[3][1] <= pos[1] <= water_pos[1][1]):
                player[5] = 3  # 泡泡狀

                # 設定5秒後若還是泡泡狀 則dead  加到 一個list 若被救 timer 要刪除

                def time_to_dead(person, ind):
                    if person[5] == 3:
                        person[5] = 4
                        self.all_change.append({
                            'header': 'player_dead',
                            'idx': ind,
                            'player': person[3]
                        })
                    reply = self.get_change()
                    for client in self.client:
                        client.send(json.dumps(reply).encode('utf-8'))

                ttt = Timer(5, time_to_dead, [player, idx])
                ttt.start()

                #
                buble_player_pos.append([player[3]])
                buble_player_idx.append(idx)
        # end
        # 變泡泡用位置判斷
        self.waterball.remove([x, y])
        self.all_change.append({
            'header': 'water_area',
            'area': water_pos,
            'position': (x, y),
            'player_to_bubble_pos': buble_player_pos,
            'player_to_bubble_idx': buble_player_idx,
        })

    def end_bomb(self, x, y):
        self.all_change.append({
            'header': 'end_bomb',
            'position': [x, y]
        })

    def cell_colidsion(self, x, y):
        for posx, posy in self.cell_solidobj:
            if x == posx and y == posy:
                return True
        return False

    def change_direction(self, player_num, direction):
        self.player[player_num][6] = direction
        self.all_change.append({
            'header': 'player',
            'idx': player_num,
            'direction': direction
        })

    def get_change(self):
        temp = copy.deepcopy(self.all_change)
        self.all_change = []
        temp = {
            'data': temp
        }
        return temp

    def get_max_pos(self, x, y, power):
        center_x, center_y = x, y
        lx, ly = x - power, y
        rx, ry = x + power, y
        fx, fy = x, y + power
        bx, by = x, y - power

        # left max
        for now in range(x, -1, -1):
            if now == lx:
                break
            if now == 0:
                lx = 0
                break
            if self.cell_colidsion(now, ly):
                lx = now + 1
                break
        # right max
        for now in range(x, self.cellmap[0], 1):
            if now == rx:
                break
            if now == self.cellmap[0] - 1:
                rx = now
                break
            if self.cell_colidsion(now, ry):
                rx = now - 1
                break
        # back max
        for now in range(y, -1, -1):
            if now == by:
                break
            if now == 0:
                by = 0
                break
            if self.cell_colidsion(bx, now):
                by = now + 1
                break
        # forword max
        for now in range(y, self.cellmap[1], 1):
            if now == fy:
                break
            if now == self.cellmap[1] - 1:
                fy = now
                break
            if self.cell_colidsion(fx, now):
                fy = now - 1
                break
        return [[lx, ly], [bx, by], [rx, ry], [fx, fy]]  # 因為坐標系不同，上下交換
