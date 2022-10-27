from enum import unique

from app.models.ability import Ability
from app.models.form import Form
from app.models.move import Move
from django.db import models


class Pokemon(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    abilities = models.ManyToManyField(Ability)
    forms = models.ManyToManyField(Form)
    moves = models.ManyToManyField(Move)
