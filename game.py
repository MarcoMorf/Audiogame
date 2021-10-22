#!/usr/bin/env python
""" pygame.examples.sprite_texture
Experimental! Uses APIs which may disapear in the next release (_sdl2 is private).
Hardware accelerated Image objects with pygame.sprite.
_sdl2.video.Image is a backwards compatible way with to use Texture with
pygame.sprite groups.
"""
import os
import pygame as pg
from math import sin, cos, radians
import random

import queue
import threading
import time



if pg.get_sdl_version()[0] < 2:
    raise SystemExit("This example requires pygame 2 and SDL2.")
from pygame._sdl2 import Window, Texture, Image, Renderer

from audio import listen

angular_speed = 1

data_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], "data")


def load_img(file):
    return pg.image.load(os.path.join(data_dir, file))

class Something(pg.sprite.Sprite):
    def __init__(self, img):
        pg.sprite.Sprite.__init__(self)

        self.rect = img.get_rect()
        self.image = img

        self.rect.w *= 5
        self.rect.h *= 5

        
        img.origin = self.rect.w / 4, self.rect.h / 2

        self.velocity_projectile = [1.0,-1.0]

class Target(pg.sprite.Sprite):
    def __init__(self, img):
        pg.sprite.Sprite.__init__(self)

        self.rect = img.get_rect()
        self.image = img

        self.rect.w *= 1.3
        self.rect.h *= 1.3


pg.display.init()
pg.key.set_repeat(10, 10)

win = Window("asdf", resizable=True)
renderer = Renderer(win)

tex = Texture.from_surface(renderer, load_img("shot.gif"))
tex_target = Texture.from_surface(renderer, load_img("chimp.bmp"))

global game_round, target_position
target_position = random.randrange(300, 750)
game_round = 0
num_players = 2

def main():
    global game_round, target_position
    if game_round % num_players == 0:
        target_position = random.randrange(300, 750)
    game_round += 1

    sprite_target = Target(Image(tex_target))
    sprite_target.rect.x = target_position
    sprite_target.rect.y = 400.0
    sprite_target.rect.w /= 2.0
    sprite_target.rect.h /= 2.0        

    sprite = Something(Image(tex))
    sprite.rect.x = 100.0
    sprite.rect.y = 350.0
    sprite.rect.w /= 2.0
    sprite.rect.h /= 2.0
    sprite.image.angle = 45

    group = pg.sprite.Group()
    group.add(sprite)
    group.add(sprite_target)

    t = 0
    running = True
    clock = pg.time.Clock()
    renderer.draw_color = (10, 10, 10, 255)

    rotation_cw = True

    flying = False
    y_pos = 0
    # launch_speed = 6

    # Audio setup

    bounce_queue = queue.Queue()

    worker = threading.Thread(target=listen, args=(bounce_queue,), daemon=True)
    cannon_stopped = False
    listening = False

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN and event.key == pg.K_UP and not listening:
                worker.start()
                listening = True

        try:
            item = bounce_queue.get_nowait()
        except queue.Empty:
            item = 0

        if item > 700:
            print("Boooom, too much")
            main()
            break

        if item == -1:
            cannon_stopped = True
            print("Angle: " + str(sprite.image.angle))

        elif item > 0:
            launch_speed = 8 * (item - 100) / 600
            flying = True
            y_pos = sprite.rect.y
            angle = radians(sprite.image.angle)
            sprite.velocity_projectile[1] = cos(angle) * launch_speed * -1
            sprite.velocity_projectile[0] = sin(angle) * launch_speed

        renderer.clear()
        t += 1

        img = sprite.image

        if flying:
            sprite.rect.x += sprite.velocity_projectile[0]
            y_pos += sprite.velocity_projectile[1]
            sprite.velocity_projectile[1] += 0.03
            sprite.rect.y = y_pos

            if sprite.rect.y > 400:
                dist = abs(sprite_target.rect.x - sprite.rect.x)
                print("Monkey: " + str(int(dist)))
                print("Distance: " + str(int(sprite_target.rect.x - 100)))
                if dist < 20:
                    print("YOU WON A GOLD MEDAL!!!!")
                elif dist < 50:
                    print("YOU WON A SILVER MEDAL!!")
                elif dist < 100:
                    print("YOU WON A BRONZE MEDAL..")
                else:
                    print("You played the game, badly.")
                main()
                break
        
        elif not cannon_stopped:
            if rotation_cw:
                img.angle += angular_speed
            else:
                img.angle -= angular_speed

            if img.angle > 80 and rotation_cw:
                rotation_cw = False
            elif img.angle < 10 and not rotation_cw:
                rotation_cw = True
        
        group.draw(renderer)
        renderer.present()

        clock.tick(60)
        win.title = str("FPS: {}".format(clock.get_fps()))

    pg.quit()

if __name__ == "__main__":
    main()