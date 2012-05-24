"""Definitions for game units and unit interaction"""
from collections import namedtuple
from stone import Stone
from weapons import *
from units import *

class Loc(namedtuple('Loc', 'x y')):
    __slots__ = ()
    def __repr__(self):
        return '(%r, %r)' % self
noloc = Loc(None,None)

