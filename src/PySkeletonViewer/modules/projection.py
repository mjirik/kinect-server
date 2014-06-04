#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Canvas and projection dynamics.
"""
import copy
import math
import os
import threading#from threading import Thread, Timer

import pygame
from pygame.locals import *
from pygame import Rect

from PySkeletonViewer.modules.sprites import Skeleton

########################################################################
########################################################################
########################################################################

FPS = 50
VIEW_WIDTH = 2400.
VIEW_HEIGHT = 1800.
X = 20
Y = 20
WIDTH = 1024.
HEIGHT = 768.
WIDTH_RATIO = WIDTH/VIEW_WIDTH
HEIGHT_RATIO = HEIGHT/VIEW_HEIGHT
COLORS = [("white"),
          "green",
          "yellow",
          "purple",
          "orange",
          "red",
          "cyan",
          "pink",
          "grey"]

########################################################################
########################################################################
########################################################################

class ProjectionCanvas(object):
    def __init__(self, app):
        #Thread.__init__(self)
        self.app = app
        
        self.x = X
        self.y = Y
        self.width = int(WIDTH)
        self.height = int(HEIGHT)
        
        self.clock = None
        self.screen = None
        self.timer = None
        
        self.background = None
        self.skeletons = pygame.sprite.RenderClear()
        self.skeleton_list = []
        self.loop_thread = threading.Thread(target = self.loop)

#####################################################
#####################################################

    def load(self):
        """Pygame initialization and screen setup"""
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.x, self.y)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('SkeletonViewer Show')
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        pygame.display.update()
        self.set_background()

#####################################################
#####################################################

    def start(self):
        print "LOOP STARTED"
        self.loop_thread.start()

    def set_background(self):
        """Load image and blits it into the background"""
        pygame.init()
        self.background = pygame.transform.scale(pygame.image.load(
            os.path.abspath(os.path.join(self.app.path, "PySkeletonViewer", "images",
            "bg.png"))).convert(),(self.width, self.height))
        self.screen.blit(self.background, (0,0))

#####################################################
#####################################################

    def mode_clear(self):
        """Clears all the sprites"""
        self.skeletons.clear(self.screen, self.background)

#####################################################
#####################################################

    def loop(self):
        """Refreshes the screen and animations"""
        while self.app.projecting:
            time_passed = self.clock.tick(FPS)
            self.draw_skeletons()
#            self.mode_clear()
#            self.update()
#            self.skeletons.draw(self.screen)
           
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.app.main_window.stop_projection()

#####################################################
#####################################################

    def draw_skeletons(self):
        #surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.screen.fill((0,0,0,1))
        for i, skeleton in enumerate( self.app.skeletons):
            if len(skeleton.keys()) > 0:
                self.draw_skeleton(skeleton, COLORS[i])

    def draw_skeleton(self, body, color):
        self.draw_head(body, color)
        self.draw_body(body, color)
        self.draw_right_arm(body, color)
        self.draw_left_arm(body, color)
        self.draw_right_leg(body, color)
        self.draw_left_leg(body, color)

#####################################################
#####################################################

    def draw_line(self, color, p1, p2):
        pygame.draw.line(self.screen, Color(color), p1, p2, 5)

#####################################################
#####################################################

    def draw_head(self, body, color):
        """Draws skeletons head"""
        head = body["Head"]
        neck = body["Neck"]
        radius = int(round(math.sqrt(math.pow(head["X"] - neck["X"], 2.0) +
                                    math.pow(head["Y"] - neck["Y"], 2.0))))
        pygame.draw.ellipse(self.screen, Color(color),
            Rect(head["X"] - radius, head["Y"] - radius, 2*radius, 2*radius), 5)
        self.draw_line(color, (head["X"], head["Y"]),
            (head["X"], head["Y"]))

    ###########################################

    def draw_body(self, body, color):
        """Draws skeletons body"""
        neck = body["Neck"]
        lshoulder = body["LeftShoulder"]
        rshoulder = body["RightShoulder"]
        lhip = body["LeftHip"]
        rhip = body["RightHip"]
        torso = body["Torso"]
        pelvis_x = int(round(float(rhip["X"] + lhip["X"])/2.))
        pelvis_y = int(round(float(rhip["Y"] + lhip["Y"])/2.))
        self.draw_line(color, (lshoulder["X"], lshoulder["Y"]),
            (neck["X"], neck["Y"]))
        self.draw_line(color, (rshoulder["X"], rshoulder["Y"]),
            (neck["X"], neck["Y"]))
        self.draw_line(color, (neck["X"], neck["Y"]),
                            (pelvis_x, pelvis_y))
        self.draw_line(color, (lhip["X"], lhip["Y"]),
                            (pelvis_x, pelvis_y))
        self.draw_line(color, (rhip["X"], rhip["Y"]),
                            (pelvis_x, pelvis_y))



#        self.draw_line(color, (lshoulder["X"], lshoulder["Y"]),
#            (torso["X"], torso["Y"]))
#        self.draw_line(color, (rshoulder["X"], rshoulder["Y"]),
#            (torso["X"], torso["Y"]))
#        self.draw_line(color, (lhip["X"], lhip["Y"]),
#            (torso["X"], torso["Y"]))
#        self.draw_line(color, (rhip["X"], rhip["Y"]),
#            (torso["X"], torso["Y"]))
#        self.draw_line(color, (lhip["X"], lhip["Y"]),
#            (rhip["X"], rhip["Y"]))

    ###########################################

    def draw_right_arm(self, body, color):
        """Draws skeletons arm"""
        rshoulder = body["RightShoulder"]
        relbow = body["RightElbow"]
        rhand = body["RightHand"]
        self.draw_line(color, (rshoulder["X"], rshoulder["Y"]),
            (relbow["X"], relbow["Y"]))
        self.draw_line(color, (rhand["X"], rhand["Y"]),
            (relbow["X"], relbow["Y"]))

    ###########################################

    def draw_left_arm(self, body, color):
        """Draws skeletons arm"""
        lshoulder = body["LeftShoulder"]
        lelbow = body["LeftElbow"]
        lhand = body["LeftHand"]
        self.draw_line(color, (lshoulder["X"], lshoulder["Y"]),
            (lelbow["X"], lelbow["Y"]))
        self.draw_line(color, (lhand["X"], lhand["Y"]),
            (lelbow["X"], lelbow["Y"]))

    ###########################################

    def draw_left_leg(self, body, color):
        """Draws skeletons leg"""
        lhip = body["LeftHip"]
        lknee = body["LeftKnee"]
        lfoot = body["LeftFoot"]
        self.draw_line(color, (lhip["X"], lhip["Y"]),
            (lknee["X"], lknee["Y"]))
        self.draw_line(color, (lknee["X"], lknee["Y"]),
            (lfoot["X"], lfoot["Y"]))

    ###########################################

    def draw_right_leg(self, body, color):
        """Draws skeletons leg"""
        rhip = body["RightHip"]
        rknee = body["RightKnee"]
        rfoot = body["RightFoot"]
        self.draw_line(color, (rhip["X"], rhip["Y"]),
            (rknee["X"], rknee["Y"]))
        self.draw_line(color, (rknee["X"], rknee["Y"]),
            (rfoot["X"], rfoot["Y"]))













































        #####################################################
        ##########################################################################################################
        ##########################################################################################################
        #####################################################


    def update(self):
        """Custom update - handles the amount of skeletons and updates every one of them"""
        print "updating skels", len(self.app.skeletons)
        #skeletons = self.app.skeletons
        print "update done"
#        if len(self.skeleton_list) > len(skeletons):
#            missing_skel = self.skeleton_list.pop(len(self.skeleton_list) - 1)
#            self.skeletons.remove(missing_skel)
#        elif len(self.skeleton_list) < len(skeletons):
#            i = len(self.skeleton_list) - 1
#            new_skel_data = skeletons[i]
#            sprite_data, head_radius = self.place_skeleton(new_skel_data)
#            new_skeleton = Skeleton(sprite_data, COLORS[i], head_radius, Rect(0,0, self.width, self.height))
#            self.skeleton_list.append(new_skeleton)
#            self.skeletons.add(new_skeleton)
#        for i, skeleton in enumerate(self.skeleton_list):
#            skel_data = skeletons[i]
#            sprite_data, head_radius = self.place_skeleton(skel_data)
#            skeleton.update(sprite_data, head_radius)
            
#####################################################
#####################################################

    def place_skeleton(self, body):
        """Finds the place for the skeleon on the screen.
           Handles the screen resize"""
        if len(body.keys()) is not 0:
            sprite_data = copy.deepcopy(body)
            for joint in sprite_data.keys():
                sprite_data[joint]["X"] = int(round((sprite_data[joint]["X"] + VIEW_WIDTH/2.)*WIDTH_RATIO))
                sprite_data[joint]["Y"] = int(round((sprite_data[joint]["Y"] - VIEW_HEIGHT/2.)*HEIGHT_RATIO))

            head_radius = math.sqrt(math.pow(sprite_data["Head"]["X"] - sprite_data["Neck"]["X"], 2.0) +
                                        math.pow(sprite_data["Head"]["Y"] - sprite_data["Neck"]["Y"], 2.0))
            return (sprite_data, head_radius)
        else:
            return ({}, 0)

#            print body.keys()
#            left = body[body.keys()[0]]["X"]
#            top = body[body.keys()[0]]["Y"]
#            right = body[body.keys()[0]]["X"]
#            bottom = body[body.keys()[0]]["Y"]
#
#            for joint in body.keys()[1:]:
#                if body[joint]["X"] < left:
#                    left = body[joint]["X"]
#                elif body[joint]["X"] > right:
#                    right = body[joint]["X"]
#                if body[joint]["Y"] < bottom:
#                    bottom = body[joint]["Y"]
#                elif body[joint]["Y"] > top:
#                    top = body[joint]["Y"]
#
#            sprite_data = copy.deepcopy(body)
#            for joint in sprite_data.keys():
#                sprite_data[joint]["X"] -= left
#                sprite_data[joint]["X"] = int(round(float(sprite_data[joint]["X"])*WIDTH_RATIO))
#                sprite_data[joint]["Y"] -= bottom
#                sprite_data[joint]["Y"] = int(round(float(sprite_data[joint]["Y"])*HEIGHT_RATIO))
#
#            head_radius = math.sqrt(math.pow(sprite_data["Head"]["X"] - sprite_data["Neck"]["X"], 2.0) +
#                            math.pow(sprite_data["Head"]["Y"] - sprite_data["Neck"]["Y"], 2.0))
#
#            bottom = bottom - head_radius
#            width = int(round(float(right - left)*WIDTH_RATIO))
#            height = int(round(float(top - bottom)*HEIGHT_RATIO))
#
#            position = (int(round(float(left)*WIDTH_RATIO)),
#                        int(round(float(bottom)*HEIGHT_RATIO)))
#            ret_val = (width, height, position, sprite_data, head_radius)
#        else:
#            ret_val = (0, 0, 0, 0, 0)
#        print "placed"
#        return ret_val
        
        
#####################################################
#####################################################

    def finish(self):
        """Pygame quit"""
        self.app.projecting = False
        pygame.init()
        pygame.display.quit()
        #self.skeletons.empty()
