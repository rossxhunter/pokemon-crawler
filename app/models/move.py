from django.db import models


class Move(models.Model):
    name = models.CharField(max_length=255, unique=True)
