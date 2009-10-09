import pygame
from pygame.locals import *
from battlefield import Battlefield
import defs

class board(width, length):
    """displays a battlefield for user interaction"""
    def __init__(self):
        self.b = Battlefield()
        self.width = width
        self.length = length

