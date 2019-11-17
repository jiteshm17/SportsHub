from django.db import models
from user_auth.models import Profile
from django.contrib.auth.models import User


class Sport_Info(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(max_length=1000, blank=True, null=True)
    objective = models.TextField(max_length=1000, blank=True, null=True)
    equipment = models.TextField(max_length=2000, blank=True, null=True)
    scoring = models.TextField(max_length=1000, blank=True, null=True)
    winning_criteria = models.TextField(max_length=1000, blank=True, null=True)
    rules = models.TextField(max_length=10000, blank=True, null=True)
    image = models.ImageField(upload_to='static/sports/sport-image', blank=True)
    playlist=models.CharField(max_length=100,blank=True,null=True)
    icon = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.name


class FavoriteSports(models.Model):
    sport = models.ForeignKey(Sport_Info, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sport', 'user')

    def __str__(self):
        return self.sport


class Tournaments(models.Model):
    image = models.ImageField(upload_to='static/sports/Tournament_Images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(max_length=1000)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    no_of_joined = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class CoachingCenters(models.Model):
    image = models.ImageField(upload_to='static/sports/Coachingcenters_Images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(max_length=1000)
    street_name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.PositiveIntegerField()
    phone_num = models.BigIntegerField()
    mail = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name


class TournamentJoin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, null=False)
    mail = models.EmailField(blank=False, null=False)
    phoneNumber = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
