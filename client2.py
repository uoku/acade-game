import socket, sys, json, pickle, threading
import pygame

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
client.connect((host, 8888))


def listen():
    while True:
        m = client.recv(10000)
        if m:
            m = m.decode('utf-8')
            print(m)


t = threading.Thread(target=listen)
t.start()

pygame.init()
win = pygame.display.set_mode((320, 240))
pygame.display.set_caption("first game")
run = True

while True:

    pygame.time.delay(15)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    move = None
    if keys[pygame.K_LEFT]:
        move = 3
    if keys[pygame.K_DOWN]:
        move = 2
    if keys[pygame.K_UP]:
        move = 0
    if keys[pygame.K_RIGHT]:
        move = 1
    if keys[pygame.K_SPACE]:
        move = 4
    pygame.display.update()

    if move is not None:
        client.send(json.dumps(str(move)).encode('utf-8'))
