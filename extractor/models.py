from django.db import models

class Experiment(models.Model):
    flow_rate = models.FloatField()
    rpm = models.IntegerField()

    initial_water_conc = models.FloatField()
    initial_oil_conc = models.FloatField()

    final_water_conc = models.FloatField()
    final_oil_conc = models.FloatField()

    efficiency = models.FloatField()

    def __str__(self):
        return f"RPM: {self.rpm}, Flow: {self.flow_rate}"