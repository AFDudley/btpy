from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import transaction
#ZODB needs to log stuff
import logging
logging.basicConfig()
from binary_tactics.world import *

#def new_player(username):
    #"""Inserts a new user into ZODB"""
    #pass
if __name__ == '__main__':
    storage = FileStorage('ZODB/Data.fs')
    db = DB(storage)
    connection = db.open()
    root = connection.root()

    w = World(username='World')
    #w.make_grids(root) 
    