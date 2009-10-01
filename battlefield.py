import os, sys # for clearing the screen

class Grid(object):
    def __init__(self):
        self.units = {}
        self.tiles = {}

    def place_unit(self, u, tile):
        """Places unit u at tile (x,y)"""
        self.units[u] = tile
        self.tiles[tile] = u

    def move_unit(self, u, tile):
        """Moves unit u from its current location to tile"""
        del self.tiles[self.units[u]]
        self.tiles[tile] = u
        self.units[u] = tile

    def get_unit(self, u):
        """Returns the location of unit u"""
        return self.units[u]

    def get_tile(self, tile):
        """Returns the object at tile location (x,y)"""
        return self.tiles[tile]

    def remove_unit(self, u):
        """Removes the unit from the tile it is on"""
        del self.tiles[self.units[u]]
        del self.units[u] #XXX: maybe just assign to None, don't delete it

    def clear_tile(self, tile):
        """Clears the unit from tile (x,y)"""
        del self.units[self.tiles[tile]] #XXX: maybe just assign to None, don't delete it
        del self.tiles[tile]

class Battlefield(Grid):
    """A battlefield is a map of tiles which contains units and the logic for their movement and status."""
    def __init__(self):
        self.graveyard = []
        self.clock = 0
        self.ticking = False
        self.queue = []
        self.status_effects = []
        super(Battlefield, self).__init__()

    def place_unit(self, unit, tile):
        """Places unit at tile (x,y), raises exception if a unit is already on that tile"""
        x,y = tile
        if not tile in self.tiles:
            super(Battlefield, self).place_unit(unit, tile)
        else:
            raise Exception("Unit already in place on that tile")

    def kill_unit(self, tile):
        """Kills the unit at tile (x,y), raises exception if no unit is found"""
        x,y = tile
        if self.grid[x][y] != None:
            self.graveyard.append(self.grid[x][y])
            self.grid[x][y] = None #TODO: drop that unit's stone at this tile
        else:
            raise Exception("No unit found at that tile")

    def move_unit(self, unit, tile):
        x,y = tile
        if not tile in self.tiles:
            x0,y0 = self.get_unit(unit)
            if abs(x-x0) + abs(y-y0) <= unit.move:
                super(Battlefield, self).move_unit(unit, tile)
                pass
            else:
                raise Exception("Moved too many spaces")

    def process(self, command):
        """Process a battle command (move, act, or both) for unit"""
        fst_cmd, fst_args = command[0]
        snd_cmd, snd_args = command[1]
        fst_cmd(*fst_args)
        snd_cmd(*snd_args)

    def act(self, action, args):
        action(*args)

    def start(self):
        self.ticking = True
        raise NotImplementedError

################################################################################

class Cursor:
    # Notes: The WASD keys are used for movement for now until I can figure out how to implement
    # arrow-key input and mouse input. There is no support for unbuffered input yet, so the user must
    # press the <enter> key after entering each command. Future versions will fix these issues.
    def __init__(self, xPos, yPos):
        self.xPos = 0
        self.yPos = 0

    def showPos(self):
        print "Position: (%s,%s)" % (self.xPos, self.yPos)

    def getDirection(self):
        direction = raw_input("Direction: ");

        if direction == 'w' or direction == 'W':
              if self.yPos > 0:
                  self.yPos -= 1
        elif direction == 'a' or direction == 'A':
              if self.xPos > 0:
                  self.xPos -= 1
        elif direction == 's' or direction == 'S':
              if self.yPos < 15:
                  self.yPos += 1
              sys.stdout.write(os.popen('clear').read())
        elif direction == 'd' or direction == 'D':
            if self.xPos < 15:
                self.xPos += 1
            else:
                print "Invalid input."

if __name__ == "__main__":
    cursor = Cursor(0, 0) # Start at (0,0)
    quit = 0

    while quit == 0:
        sys.stdout.write(os.popen('clear').read()) # clear the screen
        cursor.showPos() # print current position
        cursor.getDirection() # get direction from user
