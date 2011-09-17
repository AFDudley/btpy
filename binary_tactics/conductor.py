from multiprocessing import Process
from random import randrange
import time

class conductor(Process):
    def __init__(self):
        Process.__init__(self)