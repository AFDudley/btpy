from equanimity.world import *
world = World()
world.players = world.root['Players']


#Be sure to create the users via the web w/test_client.signup
#defender setup
world.award_field('World', '(0, 0)', 'dfndr')
f = world.players['dfndr'].wFields['(0, 0)']
world.populate_defenders(f)

#atkr setup
world.award_field('World', '(0, 1)', 'atkr')
f2 = world.players['atkr'].wFields['(0, 1)']
world.populate_squads(f2)

#prepare battlequeue
world.move_squad(f2, f2.stronghold.squads.keys()[0], f)
