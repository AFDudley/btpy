"""Test the Battlefield/Grid implementations"""

from battlefield import Battlefield
from defs import Item, Stone, Unit, Scient, Nescient, ELEMENTS, E, F, I, W
from defs import test_skill

## helpers #####################################################################

def rand_unit(name="Dummy"):
    """Creates a random unit with some crappy stats"""
    import random
    comp1, comp2 = (random.randint(0,100), random.randint(0,100))
    unit = Scient(random.choice(ELEMENTS), {E:comp1, F:comp2, I:100-comp2, W:100-comp1})
    unit.name = name
    return unit

## tests #######################################################################

def test_init():
    b = Battlefield()
    assert b.graveyard == []
    assert b.ticking == False
    assert b.queue == []
    assert b.clock == 0

def test_singleton():
    """Test to make sure that only one instance of a unit exists at a time"""
    u = rand_unit("Alice")
    b = Battlefield()
    b.place_unit(u, (0,0))
    assert b.get_tile((0,0)) is u
    u.name = "Bob"
    assert b.get_tile((0,0)).name == u.name

def test_place_unit():
    u1 = rand_unit("Alice")
    u2 = rand_unit("Bob")
    b = Battlefield()
    b.place_unit(u1, (0,0))
    b.place_unit(u2, (10,10))
    assert b.get_tile((0,0)).name == "Alice"
    assert b.get_tile((10,10)).name == "Bob"

def test_place_failure():
    u1 = rand_unit("Alice")
    u2 = rand_unit("Charles")
    b = Battlefield()
    b.place_unit(u1, (0,0))
    try:
        b.place_unit(u2, (0,0))
    except Exception, e:
        msg = str(e)
        assert msg == "Unit already in place on that tile"
        assert b.get_tile((0,0)).name == "Alice"
        assert u2.name == "Charles"

def test_remove_unit():
    u1 = rand_unit("Alice")
    b = Battlefield()
    b.place_unit(u1, (5,5))
    assert b.get_tile((5,5)).name == "Alice"
    b.remove_unit(u1)
    assert not u1 in b.units

def test_move_unit():
    u1 = rand_unit("Alice")
    b = Battlefield()
    b.place_unit(u1, (0,0))
    b.move_unit(u1, (2,2))
    assert b.get_unit(u1) == (2,2)
    assert b.get_tile((2,2)).name == "Alice"
    try:
        #this should fail
        b.get_tile((0,0))
    except KeyError:
        #ok!
        pass

def test_process_cmd():
    u1 = rand_unit("Alice")
    u2 = rand_unit("Bob")
    u1.element = "test"
    u2.element = "test"
    b = Battlefield()
    b.place_unit(u1, (0,0))
    b.place_unit(u2, (1,0))
    hp_before = u2.hp
    b.process(
                 ((b.move_unit, (u1, (0,0))),
                  (b.act, (u1.strikes, ((1,0), 1, "test", b)))
                 )
             )
    assert u2.hp < hp_before
