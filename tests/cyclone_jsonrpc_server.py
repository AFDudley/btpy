#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys
import cyclone.web
import cyclone.httpclient
from twisted.python import log
from twisted.internet import reactor, defer

from binary_tactics.hex_battle import *
from stores.yaml_store import *
from binary_tactics.hex_battlefield import Battlefield
from binary_tactics.player import Player

class MainHandler(cyclone.web.RequestHandler):
    def get(self):
        self.write("Welcome to the battle!")
    ####

class BattleHandler(cyclone.web.JsonrpcRequestHandler):
    @defer.inlineCallbacks
    def jsonrpc_process_action(self, args):
        #obviously this needs to be more robust.
        #so nasty.
        action = Action(eval(args[0]), args[1], eval(args[2]))
        return game.process_action(action)

    @defer.inlineCallbacks
    def jsonrpc_get_state(self):
        return game.state

    @defer.inlineCallbacks
    def jsonrpc_initial_state(self):
        return str(game.initial_state()) #should NOT be a string.


def main():
    application = cyclone.web.Application([
        (r"/", MainHandler),
        (r"/battle", BattleHandler),
    ])
    
    reactor.listenTCP(8888, application)
    reactor.run()
    
    print game.state
    
if __name__ == "__main__":
    #battle setup.
    p1   = Player(name='p1', squads=[load('yaml/ice_maxes.yaml')])
    p2   = Player(name='p2', squads=[load('yaml/fire_maxes.yaml')])
    game = Game(player1=p1, player2=p2,
                battlefield=Battlefield(squad1=p1.squads[0],
                squad2=p2.squads[0]),)
    btl = game.battlefield
    
    for s in range(2):
        for x in range(4):
            btl.place_object(btl.squads[s][x], defs.Loc(x, s))
    
    game.log['init_locs'] = game.log.init_locs()
    print game.state
    log.startLogging(sys.stdout)
    main()
