from django.db import models

class Experiment(models.Model):
    flow_rate = models.FloatField()
    rpm = models.IntegerField()
    water_conc = models.FloatField()
    acetone_conc = models.FloatField()
    reynolds = models.FloatField()
    efficiency = models.FloatField()

    def __str__(self):
        return f"RPM: {self.rpm}, Flow: {self.flow_rate}"
# Create your models here.
