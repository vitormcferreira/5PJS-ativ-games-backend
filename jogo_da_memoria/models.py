from django.db import models
from accounts.models import Usuario


class Ranking(models.Model):
    usuario = models.ForeignKey(to=Usuario, on_delete=models.CASCADE)
    jogadas = models.IntegerField()
    erros = models.IntegerField()
