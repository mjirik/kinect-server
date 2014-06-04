#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Animation classes - Sprites.
"""
import os

import pygame
from pygame.sprite import Sprite
from pygame import Rect, Color

########################################################################
########################################################################
########################################################################

HEAD_RADIUS = 0.75

########################################################################
########################################################################
########################################################################

class Skeleton(Sprite):
    def __init__(self, body, color, rect):
        Sprite.__init__(self)
        self.body = body
        self.color = color
        self.image = None
        self.rect = rect
        self.update(body, head_radius)

#####################################################
#####################################################

    def update(self, body, head_radius):
        """Main update function"""
        self.body = body
        self.redraw_skeleton(head_radius)
        #self.rect = Rect(position[0], position[1] - head_radius, width, height)

#####################################################
#####################################################

    def redraw_skeleton(self, head_space):
        """Redraws the skeleton according to the current data"""
        surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        surface.fill((255,255,255,0)) 
        self.draw_head(surface, head_space)
        self.draw_body(surface, head_space)
        self.draw_right_arm(surface, head_space)
        self.draw_left_arm(surface, head_space)
        self.draw_right_leg(surface, head_space)
        self.draw_left_leg(surface, head_space)
        self.image = surface

#####################################################
#####################################################
    
    def draw_line(self, surface, p1, p2):
        pygame.draw.line(surface, Color(self.color), p1, p2, 5)

#####################################################
#####################################################

    def draw_head(self, surface, space):
        """Draws skeletons head"""
        head = self.body["Head"]
        neck = self.body["Neck"]
        radius = int(round(float(space)*HEAD_RADIUS))
        pygame.draw.ellipse(surface, Color(self.color),
                Rect(head["X"] - radius,
                head["Y"] - radius + space, 2*radius, 2*radius), 5)
        self.draw_line(surface, (head["X"], head["Y"] + space),
                                (head["X"], head["Y"] + space))
        
        self.draw_line(surface, (head["X"], head["Y"] + space),
                                (neck["X"], neck["Y"] + space))
        
###########################################

    def draw_body(self, surface, space):
        """Draws skeletons body"""
        neck = self.body["Neck"]
        lshoulder = self.body["LeftShoulder"]
        rshoulder = self.body["RightShoulder"]
        lhip = self.body["LeftHip"]
        rhip = self.body["RightHip"]
        torso = self.body["Torso"]
        self.draw_line(surface, (lshoulder["X"], lshoulder["Y"] + space),
                                (neck["X"], neck["Y"] + space))
        self.draw_line(surface, (rshoulder["X"], rshoulder["Y"] + space),
                                (neck["X"], neck["Y"] + space))
        self.draw_line(surface, (lshoulder["X"], lshoulder["Y"] + space),
                                (torso["X"], torso["Y"] + space))
        self.draw_line(surface, (rshoulder["X"], rshoulder["Y"] + space),
                                (torso["X"], torso["Y"] + space))
        self.draw_line(surface, (lhip["X"], lhip["Y"] + space),
                                (torso["X"], torso["Y"] + space))
        self.draw_line(surface, (rhip["X"], rhip["Y"] + space),
                                (torso["X"], torso["Y"] + space))
        self.draw_line(surface, (lhip["X"], lhip["Y"] + space),
                                (rhip["X"], rhip["Y"] + space))

###########################################

    def draw_right_arm(self, surface, space):
        """Draws skeletons arm"""
        rshoulder = self.body["RightShoulder"]
        relbow = self.body["RightElbow"]
        rhand = self.body["RightHand"]
        self.draw_line(surface, (rshoulder["X"], rshoulder["Y"] + space),
                                (relbow["X"], relbow["Y"] + space))
        self.draw_line(surface, (rhand["X"], rhand["Y"] + space),
                                (relbow["X"], relbow["Y"] + space))

###########################################

    def draw_left_arm(self, surface, space):
        """Draws skeletons arm"""
        lshoulder = self.body["LeftShoulder"]
        lelbow = self.body["LeftElbow"]
        lhand = self.body["LeftHand"]
        self.draw_line(surface, (lshoulder["X"], lshoulder["Y"] + space),
                                (lelbow["X"], lelbow["Y"] + space))
        self.draw_line(surface, (lhand["X"], lhand["Y"] + space),
                                (lelbow["X"], lelbow["Y"] + space))

###########################################

    def draw_left_leg(self, surface, space):
        """Draws skeletons leg"""
        lhip = self.body["LeftHip"]
        lknee = self.body["LeftKnee"]
        lfoot = self.body["LeftFoot"]
        self.draw_line(surface, (lhip["X"], lhip["Y"] + space),
                                (lknee["X"], lknee["Y"] + space))
        self.draw_line(surface, (lknee["X"], lknee["Y"] + space),
                                (lfoot["X"], lfoot["Y"] + space))

###########################################

    def draw_right_leg(self, surface, space):
        """Draws skeletons leg"""
        rhip = self.body["RightHip"]
        rknee = self.body["RightKnee"]
        rfoot = self.body["RightFoot"]
        self.draw_line(surface, (rhip["X"], rhip["Y"] + space),
                                (rknee["X"], rknee["Y"] + space))
        self.draw_line(surface, (rknee["X"], rknee["Y"] + space),
                                (rfoot["X"], rfoot["Y"] + space))