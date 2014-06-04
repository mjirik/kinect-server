#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Animation classes - Sprites.
"""
import os
import threading

import pygame
from pygame.sprite import Sprite
from pygame import Rect, Color


########################################################################
########################################################################
########################################################################

LAYER_FIRST = 3
LAYER_SECOND = 1
LAYER_BG = -1

HEAD_RADIUS = 0.75
ROLLING_SPEED = 5
SPEEDS = [3,
          5,
          10,
          20]
PLANE_SIZE = 1./5.
COIN_WIDTH = 1./10.
ANGLE_SEPARATOR = 15
  
########################################################################
########################################################################
########################################################################

class Plane(Sprite):
    def __init__(self, app, rect):
        Sprite.__init__(self)
        self.title = "plane"
        self.app = app
        self.screen_width = rect.width
        self.width = int(round(float(rect.width)*PLANE_SIZE))

        self.left = []
        self.right = []
        self.central = None

        self.image = self.load_all_images()
        self.rect = self.get_plane_pos(rect)
    
    def get_plane_pos(self, rect):
        x = int(round(float(rect.width)/2.))
        width = int(round(float(rect.width)*PLANE_SIZE))
        y = rect.height - width
        return Rect(x, y, width, width)
    
    def load_all_images(self):
        self.central = pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "plane.png"))), (self.width, self.width))
        self.left.append(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "left", "1.png"))), (self.width, self.width)))
        self.left.append(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "left", "2.png"))), (self.width, self.width)))
        self.left.append(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "left", "3.png"))), (self.width, self.width)))
        self.left.append(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "left", "4.png"))), (self.width, self.width)))
        
        self.right.append(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "right", "1.png"))), (self.width, self.width)))
        self.right.append(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "right", "2.png"))), (self.width, self.width)))
        self.right.append(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "right", "3.png"))), (self.width, self.width)))
        self.right.append(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "right", "4.png"))), (self.width, self.width)))
        return self.central

    def update(self, angle):
        self.set_angle(angle)
        
    def set_angle(self, angle):
        if angle > ANGLE_SEPARATOR:
            i = int((angle - angle%ANGLE_SEPARATOR)/ANGLE_SEPARATOR)
            if i > 3:
                i = 3
            self.rect.x = self.rect.x - SPEEDS[i]
            self.image = self.left[i]
        elif angle < -ANGLE_SEPARATOR:
            i = int((angle - angle%(-ANGLE_SEPARATOR))/(-ANGLE_SEPARATOR))
            if i > 3:
                i = 3
            self.rect.x = self.rect.x + SPEEDS[i]
            self.image = self.right[i]
        else:
            self.image = self.central
        if self.rect.x < 0:
            print "improving rect"
            self.rect.x = 0
        elif self.rect.x > self.screen_width - self.width:
            print "deproving rect"
            self.rect.x = self.screen_width - self.width

########################################################################
########################################################################
########################################################################

class PlaneBack(Sprite):
    def __init__(self, width):
        Sprite.__init__(self)
        self.title = "plane_back"
        self.width = width
        
        self.left = []
        self.right = []
        self.central = None
        
        self.image = self.load_all_images()
        self.rect = Rect(0,0,0,0)
    
    def load_all_images(self):
        self.central = pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "plane_back.png")))
        self.left.append(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "left", "1back.png"))))
        self.left.append(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "left", "2back.png"))))
        self.left.append(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "left", "3back.png"))))
        self.left.append(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "left", "4back.png"))))
        self.right.append(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "right", "1back.png"))))
        self.right.append(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "right", "2back.png"))))
        self.right.append(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "right", "3back.png"))))
        self.right.append(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "plane", "right", "4back.png"))))
        return self.central
    
    def update(self, angle):
        self.set_angle(angle)
        
    def set_angle(self, angle):
        if angle < 15 or angle > -15:
            self.image = self.central
        elif angle >=15 and angle < 35:
            self.image = self.left[0]
        elif angle >=35 and angle < 55:
            self.image = self.left[1]
        elif angle >=55 and angle < 75:
            self.image = self.left[2]
        elif angle >=75 and angle < 90:
            self.image = self.left[3]
        elif angle > 90 and angle < 105:
            self.image = self.right[0]
        elif angle >=105 and angle < 125:
            self.image = self.right[1]
        elif angle >=125 and angle < 145:
            self.image = self.right[2]
        elif angle >=145 and angle < 165:
            self.image = self.right[3]
            
########################################################################
########################################################################
########################################################################

class DynamicBackground(Sprite):
    def __init__(self, bg, width, group):
        self.title = "bg"
        self.groups = group
        self._layer = LAYER_BG
        Sprite.__init__(self)
        self.bg = bg
        self.width = width
        self.height = 0
        self.image = self.resize_bg()
        self.rect = Rect(0,0,0,0)
        
    def resize_bg(self):
        pygame.init()
        bg = pygame.image.load(self.bg)
        ratio = float(self.width)/float(bg.get_width())
        width = self.width
        height = int(round(float(bg.get_height())*ratio))
        self.height = height
        self.rect = Rect(0,0,width,height)
        return pygame.transform.scale(bg,(width,height))
    
    def update_rect(self, rect):
        self.rect = rect
        
########################################################################
########################################################################
########################################################################

class AltitudeIndicator(Sprite):
    def __init__(self, app, rect):
        Sprite.__init__(self)
        self.title = "altitude"
        self.app = app
        self.width = rect.width
        self.top = pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "alt_top.png"))), (self.width, self.width))
        self.bottom = pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "alt_bottom.png"))), (self.width, self.width))
        self.image = pygame.Surface((self.width, self.width), pygame.SRCALPHA)
        self.get_image(0)
        self.rect = rect
    
    def update(self, angle):
        self.get_image(angle)
    
    def rotate_centered(self, image, angle):
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect()
        original_rect = self.image.get_rect()
        clipped_rect = Rect(
            (rotated_rect.width - original_rect.width) / 2,
            (rotated_rect.height - original_rect.height) / 2,
            original_rect.width,
            original_rect.height,
        )
        return rotated_image.subsurface(clipped_rect)
        
    def get_image(self, angle):
        angle = -angle
        self.image.fill((255,255,255,0))
        self.image.blit(self.rotate_centered(self.bottom, angle), (0,0))
        self.image.blit(self.top, (0,0))

########################################################################
########################################################################
########################################################################

class Coin(Sprite):
    def __init__(self, app, rect):
        Sprite.__init__(self)
        self.app = app
        self.title = "coin"
        self.width = rect[2]
        self.image = pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "coin.png"))), (self.width, self.width))
        self.rect = rect

########################################################################
########################################################################
########################################################################

class Score(Sprite):
    def __init__(self, app, rect):
        Sprite.__init__(self)
        self.title = "score"
        self.app = app
        self.score = 0
        self.rect = rect
        self.coin = Coin(app, Rect(
                            self.rect[2] - 2*int(round(float(self.rect[3])*(2./5.))),
                                   int(round(float(self.rect[3])*(1./5.))),
                                   self.rect[3] - 2*int(round(float(self.rect[3])*(1./5.))),
                                   self.rect[3] - 2*int(round(float(self.rect[3])*(1./5.)))))
        self.image = pygame.Surface((self.rect[2], self.rect[3]), pygame.SRCALPHA)
        self.redraw_score()
        
    def center(self, rect1, rect2):
        rect1.centerx = rect2.centerx
        rect1.centery = rect2.centery
        return rect1
    
    def redraw_score(self):
        self.image.fill((255,255,255,0))
        self.image.blit(pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images",
            "score.png"))), (self.rect[2], self.rect[3])), (0,0))
        score_rect = Rect(int(round(float(self.rect[2])/6.)),
                          int(round(float(self.rect[2])/6.)),
                          int(round(float(self.rect[2])/2.)),
                          self.rect[3] - 2*int(round(float(self.rect[2])/6.)))
        self.image.blit(self.coin.image, self.coin.rect)
        if pygame.font:
            font = pygame.font.Font(None, 50)
            font.set_bold(True)
            text = font.render(str(self.score), 1, pygame.Color("black"))
            new_rect = self.center(text.get_rect(), score_rect)
            self.image.blit(text, new_rect)#self.center(text.get_rect(), name_rect))
