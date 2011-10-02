from twisted.protocols import amp

#world to pool commands
class do_battle(amp.Command):
    arguments = (
        ('attacker', amp.String()),
        ('defender', amp.String()),
        ('field', amp.Listof(amp.Integer()))
    )
    response = tuple()
    
class Harvest(amp.Command):
    arguments = (
        ('field', amp.Listof(amp.Integer()))
    )
    response  = tuple()
    
class start_production(amp.Command):
    arguments = (
        ('field', amp.Listof(amp.Integer()))
    )
    response   = tuple()
    
