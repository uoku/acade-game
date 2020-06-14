import math
import copy


## water ball 還沒加到solid obj

def colision(p1, p2): #p[x , y ,w ,h]
    minx1 = p1[0]-p1[2]/2
    maxx1 = p1[0]+p1[2]/2
    miny1 = p1[1]-p1[3]/2
    maxy1 = p1[1]+p1[3]/2

    minx2 = p2[0]-p2[2]/2
    maxx2 = p2[0]+p2[2]/2
    miny2 = p2[1]-p2[3]/2
    maxy2 = p2[1]+p2[3]/2
    if ( maxx1 > minx2 and maxx2 > minx1 and maxy1 > miny2 and maxy2 > miny1 ):
        return True
    else:
        return False


class Map():
    def __init__(self, x, y, w, h, playernum, solidobj):  # w,h is cell   x,y is 有幾格
        self.all_change = []
        self.timedis = 20
        self.cell = [w, h]
        self.map = [x * w, y * h]
        self.cellmap = [x, y]
        self.solidobj = solidobj
        self.cell_solidobj = []
        for obj in solidobj:
            self.cell_solidobj.append([obj[0] // w, obj[1] // w])
        # end
        self.waterball = []
        self.init_speed = 5
        self.init_waterball = 2
        self.init_power = 2
        self.size = [90, 90]
        self.status = 0
        self.player = []
        play_pos = [[0, 0], [14, 11]]
        for i in range(playernum):
            position = play_pos[i]
            direciotn = 1
            player_list = [self.init_speed, self.init_waterball, self.init_power, position, self.size, self.status,
                           direciotn]
            self.player.append(player_list)

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
            new_y = y + move_dis
        elif direct is 1:
            new_x = x + move_dis
        elif direct is 2:
            new_y = y - move_dis
        elif direct is 3:
            new_x = x - move_dis
        else:
            print("move error")
            raise
        for obj in self.solidobj:
            if colision([new_x, new_y, self.size[0], self.size[1]], [obj[0], obj[1], self.cell[0], self.cell[1]]):
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
        #撞死人判斷
        for player in self.player:
            if (player is not self.player[player_num]) and (player[5] is 3):
                if colision([player[3][0], player[3][1], player[4][0], player[4][1]],
                            [self.player[player_num][3][0], self.player[player_num][3][1],
                             self.player[player_num][4][0], self.player[player_num][4][1]]):
                    player[5] = 4
                    self.all_change.append({
                        'header': 'player_dead',
                        'player': player[3]
                    })

        # 吃東西判斷
        if new_x != x and new_y != y:
            for object in self.solidobj:
                if [object[0], object[1]] == [new_x, new_y]:
                    # object[2] 是 物品種類
                    if object[2] == 3:  # 鞋子
                        self.add_player_speed(player_num)
                        ##
                        # self.player[player_num][0] += 1
                    elif object[2] == 4:  # 水球
                        self.add_player_waterball(player_num)
                        # self.player[player_num][1] += 1
                    elif object[2] == 5:  # 威力
                        self.add_player_power(player_num)
                        # self.player[player_num][2] += 1
                    else:
                        print('eat error')
                        raise
        # 改 self.player 的 position
        self.player[player_num][3] = [new_x, new_y]
        # 加到 all change
        self.all_change.append({
            'header': 'player',
            'player': player_num,
            'position': [new_x, new_y]
        })
        #

    def change_status(self, player_num, status):
        self.player[player_num][5] = status

    def set_waterball(self, player_num):
        if self.player[player_num][1] is not 0:
            x, y = self.player[player_num][3]
            print(x,y)
            a = math.floor(x // self.cell[0])
            b = math.floor(y // self.cell[1])
            print(a,b)
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
        buble_player=[]
        for player in self.player:
            pos = player[3]
            if (water_pos[0][0] <= pos[0] <= water_pos[2][0] and pos[1] == water_pos[0][1]) or \
                    (water_pos[1][0] == pos[0] and water_pos[3][1] <= pos[1] <= water_pos[1][1]):
                player[5] = 3  # 泡泡狀
                buble_player.append([player[3]])
        # end
        #變泡泡用位置判斷
        self.waterball.remove([x, y])
        self.all_change.append({
            'header': 'water_area',
            'area': water_pos,
            'player_to_buble': buble_player
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
            'player': player_num,
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
        return [[lx, ly], [fx, fy], [rx, ry], [bx, by]]
