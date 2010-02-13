#
#  squads.py
#  
#
#  Created by RiX on 2/8/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#
"""Set of squads for use in testing"""

#0..255
#SUIT, ORTH1, ORTH2, OPP == Value
#2   , 1    , 1    , 0   == 4
#4   , 0    , 0    , 0   == 4
#128 , 63   , 63   , 0   == 254
#254 , 0    , 0    , 0   == 254


def make_sqaud(suit, comp_template, name):
    """Makes a Squad named 'name' of Four Scients of 'suit; one with each
    Weapon and a comp of 'comp template'."""