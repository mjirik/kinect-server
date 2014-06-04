#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Canvas and projection dynamics.
"""
import copy
import math
import os
import random
from threading import Thread, Timer

import pygame
from pygame.locals import *
from pygame import Rect

from KinectPlanes.modules.sprites import DynamicBackground, Plane, AltitudeIndicator, Coin, Score

########################################################################
########################################################################
########################################################################

WIDTH = 1124.
HEIGHT = 700.
FPS = 20
KIN_IMG_WIDTH = 1024.
KIN_IMG_HEIGHT = 768.
X = 20
Y = 20
WIDTH_RATIO = WIDTH/KIN_IMG_WIDTH
HEIGHT_RATIO = HEIGHT/KIN_IMG_HEIGHT
COLORS = [("white"),
          "green",
          "yellow",
          "purple",
          "orange",
          "red",
          "cyan",
          "pink",
          "grey"]
FRAME_WIDTH = 1600.
FRAME_HEIGHT = 1200.
FRAME_PX = 30.
FRAME_REL_HOR = int(round(WIDTH/FRAME_WIDTH*FRAME_PX))
FRAME_REL_VER = int(round(HEIGHT/FRAME_HEIGHT*FRAME_PX))
SIDE_AREA = int(round(WIDTH/4.))
ROLLING_SPEED = 3#int(round(HEIGHT/400.))
COUNTDOWN = 2.
PLANE_SIZE = 1./4.
COIN_WIDTH = 1./10.

########################################################################
########################################################################
########################################################################

class ProjectionCanvas(object):
    def __init__(self, app):
        self.name = "Projection Canvas"
        self.app = app
        random.seed()
        
        self.x = X
        self.y = Y
        self.width = int(WIDTH)
        self.height = int(HEIGHT)
        
        self.clock = None
        self.screen = None
        self.game_window = None
        self.info_window = None
        
        self.bg_sprites = pygame.sprite.RenderClear()
        self.backgrounds = []
        
        self.info_sprites = pygame.sprite.RenderClear()
        self.info_list = []
        
        self.sprites = pygame.sprite.RenderClear()
        self.sprites_list = []
        
        self.score = None
        #self.sprites = pygame.sprite.LayeredUpdates()
        #self.sprites.add(self.backgrounds)
        self.active_bg = 0
        self.add = 10
        self.set_backgrounds()

#####################################################
#####################################################

    def load(self):
        """Pygame initialization and screen setup"""
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.x, self.y)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.game_window = self.screen.subsurface(self.get_game_rect())
        self.info_window = self.screen.subsurface(self.get_info_rect())
        pygame.display.set_caption('KinectPlanes')
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        pygame.display.update()
        self.set_frame()
        self.add_basic_sprites()
        self.add_new_coin()
        #Thread(target=self.start).start()
            #self.game_window.get_rect().height - int(round(WIDTH/8.)), self.planes))

#####################################################
#####################################################

    def add_basic_sprites(self):
        plane = Plane(self.app, self.game_window.get_rect())
        self.sprites.add(plane)
        self.sprites_list.append(plane)
        
        indicator_rect = Rect(FRAME_REL_HOR,
                        self.height - SIDE_AREA - FRAME_REL_VER,
                        SIDE_AREA - 2*FRAME_REL_HOR,
                        SIDE_AREA - 2*FRAME_REL_HOR)
        alt_ind = AltitudeIndicator(self.app, indicator_rect)
        self.info_sprites.add(alt_ind)
        self.info_list.append(alt_ind)
        
        score_rect = Rect(FRAME_REL_HOR,
                        2*FRAME_REL_VER,
                        SIDE_AREA - 2*FRAME_REL_HOR,
                        int(round(float(SIDE_AREA)/2)))
        self.score = Score(self.app, score_rect)
        self.info_window.blit(self.score.image, self.score.rect)

#####################################################
#####################################################

    def add_new_coin(self):
        Timer(COUNTDOWN, self.add_new_coin).start()
        coin_width = int(round(float(self.game_window.get_rect().width)*COIN_WIDTH))
        position = random.randint(0, self.game_window.get_rect().width - coin_width)
        
        coin = Coin(self.app, Rect(position, 0, coin_width, coin_width))
        coin.rect.x = position
        coin.rect.y = 0
        self.sprites.add(coin)
        self.sprites_list.append(coin)
        
    def remove_sprite(self, sprite):
        self.sprites_list.remove(sprite)
        self.sprites.remove(sprite)
        del(sprite)  

#####################################################
#####################################################

    def increase_score(self):
        self.score.score += 1
        self.score.redraw_score()
        self.info_window.blit(self.score.image, self.score.rect)

#####################################################
#####################################################

    def get_game_rect(self):
        return Rect(FRAME_REL_HOR, FRAME_REL_VER,
                    self.width - 3*FRAME_REL_HOR - SIDE_AREA,
                    self.height - 2*FRAME_REL_VER)
    
    def get_info_rect(self):
        return Rect(self.width - FRAME_REL_HOR - SIDE_AREA , FRAME_REL_VER,
                    SIDE_AREA, self.height - 2*FRAME_REL_VER)

    def start(self):
        self.loop()

    def set_frame(self):
        self.screen.blit(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes",
            "images", "frame.png"))), (self.width, self.height)), (0,0))

    def set_backgrounds(self):
        """Load image and blits it into the background"""
        pygame.init()
        rect = self.get_game_rect()
        first = DynamicBackground(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "countryside.jpg")), rect.width, self.bg_sprites)
        second = DynamicBackground(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "countryside.jpg")), rect.width, self.bg_sprites)
        first.rect.y = -first.height + rect.height
        second.rect.y = -2*first.height + rect.height
        self.backgrounds.append(first)
        self.backgrounds.append(second)
        self.bg_sprites.add(first)
        self.bg_sprites.add(second)
        
#####################################################
#####################################################

    def mode_clear(self):
        """Clears all the sprites"""
        #self.bg_sprites.clear(self.game_window, self.backgrounds[self.active_bg].image)
        #self.skeletons.clear(self.screen, self.backgrounds[self.active_bg])
        #self.sprites.clear(self.game_window, self.backgrounds[self.active_bg].image)

#####################################################
#####################################################

    def loop(self):
        """Refreshes the screen and animations"""
        while self.app.projecting:
            time_passed = self.clock.tick(FPS)
            
            self.mode_clear()
            self.update()
            self.bg_sprites.draw(self.game_window)
            #self.skeletons.draw(self.screen)
            self.info_sprites.draw(self.info_window)
            self.sprites.draw(self.game_window)
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.app.main_window.stop_projection()

#####################################################
#####################################################

    def update(self):
        self.update_background()
        for sprite in self.sprites_list:
            if sprite.title == "plane":
                sprite.update(self.app.angle)
                for i in sprite.rect.collidelistall(self.sprites_list):
                    collided_sprite = self.sprites_list[i]
                    if collided_sprite.title == "coin":
                        self.increase_score()
                        self.remove_sprite(collided_sprite)
            else:
                if sprite.rect.y < self.game_window.get_rect().height:
                    sprite.rect.y += ROLLING_SPEED
                else:
                    self.remove_sprite(sprite)
                    #sprite.update()
        for sprite in self.info_list:
            if sprite.title == "amount":
                sprite.update()
            else:
                sprite.update(self.app.angle)

    def update_background(self):
        for i, bg in enumerate(self.backgrounds):
            old_rect = bg.rect
            y = old_rect.y
            y += ROLLING_SPEED
            if y >= self.game_window.get_rect().height:
                y -= 2*bg.height
            rect = Rect(old_rect.x, y,
                        old_rect.width, old_rect.height)
            bg.update_rect(rect)

#####################################################
#####################################################

    def finish(self):
        """Pygame quit"""
        pygame.init()
        pygame.display.quit()