from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50, unique=True, primary_key=True)
    locationOne = models.CharField(max_length=50, blank=True, null=True)
    locationTwo = models.CharField(max_length=50, blank=True, null=True)
    locationThree = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name
