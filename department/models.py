from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=250)
    acronym = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.acronym + " " + self.name
