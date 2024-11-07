from django.db import models


class States(models.Model):
    state = models.CharField(max_length=50, unique=True) #  New Hampshire has no tax sales
    abbreviation = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return f"{self.state} ({self.abbreviation})"
