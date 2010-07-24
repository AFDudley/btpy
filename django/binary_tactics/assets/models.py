from django.db import models

numbers = range(0,256)
max_comp = zip(numbers, numbers)
ELEMENTS = (
            ('E', 'Earth'),
            ('F', 'Fire'),
            ('I', 'Ice'),
            ('W', 'Wind'),
            )
WEAPON_KIND = (
                ('S', 'Sword'),
                ('B', 'Bow'),
                ('W', 'Wand'),
                ('G', 'Glove'),
                )
class Stone(models.Model):
    Earth = models.PositiveSmallIntegerField(choices=max_comp)
    Fire  = models.PositiveSmallIntegerField(choices=max_comp)
    Ice   = models.PositiveSmallIntegerField(choices=max_comp)
    Wind  = models.PositiveSmallIntegerField(choices=max_comp)
    
class Weapon(models.Model):
    element = models.CharField(max_length=5, choices=ELEMENTS)
    comp    = models.ForeignKey(Stone)
    kind    = models.CharField(max_length=5, choices=WEAPON_KIND)

    
class Scient(models.Model):
    element = models.CharField(max_length=5, choices=ELEMENTS)
    comp    = models.ForeignKey(Stone, related_name="comp")
    name    = models.CharField(max_length=20)
    weapon  = models.ForeignKey(Weapon)
    weapon_bonus = models.ForeignKey(Stone, related_name="weapon_bonus")
    

    