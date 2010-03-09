#
#  test_stone.py
#  
#
#  Created by RiX on 3/8/10.
#  Copyright (c) 2010 A. Frederick Dudley. All rights reserved.
#

from binary_tactics import defs
from binary_tactics.const import ELEMENTS
class test_stone:
    def setUp(self):
        self.stone = defs.Stone()
    
    def tearDown(self):
        del self.stone
    
    def test_elements(self):
        for x in ELEMENTS:
            assert self.stone[x] == 0

    def test_hashable(self):
        assert self.stone.__hash__()