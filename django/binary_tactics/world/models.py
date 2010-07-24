from django.db import models
from django.contrib.auth.models import User
from assets.models import Stone, Weapon, Scient
class Player(models.Model):
    """User with additional settings."""
    user = models.ForeignKey(User, unique=True)
    stones = models.ManyToManyField(Stone, symmetrical=False)
