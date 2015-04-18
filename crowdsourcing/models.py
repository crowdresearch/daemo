from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
class RegistrationModel(models.Model):
    #user = models.ForeignKey(User, unique=True)
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    created = models.DateTimeField(default=timezone.now)


class PasswordResetModel(models.Model):
    #user = models.ForeignKey(User, unique=True)
    user = models.OneToOneField(User)
    reset_key = models.CharField(max_length=40)
    created = models.DateTimeField(default=timezone.now)

class Region(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=16)

class Country(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=8)
    region = models.ForeignKey(Region)

class City(models.Model):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(Country)

class Address(models.Model):
    street = models.CharField(max_length=128)
    country = models.ForeignKey(Country)
    city = models.ForeignKey(City)

class Role(models.Model):
    name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)


class UserProfile(User):
    gender = models.SmallIntegerField(null=True)
    address = models.ForeignKey(Address, null=True)
    birthday = models.DateField(null=True)
    nationality = models.ManyToManyField(Country)
    verified = models.BooleanField(default=False)
    picture = models.BinaryField(null=True)
    friends = models.ManyToManyField('self', through='Friendship',
                                      symmetrical=False) #through_fields=('user_source','user_target'),
    roles = models.ManyToManyField(Role, through='UserRoles')
    #def __init__(self):
        #super().__init__()

class Skill(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=512)
    verified = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True)

class Worker(UserProfile):
    skills = models.ManyToManyField(Skill, through='WorkerSkill')
    #to be extended, otherwise unnecessary

class WorkerSkill(models.Model):
    worker = models.ForeignKey(Worker)
    skill = models.ForeignKey(Skill)
    level = models.IntegerField(null=True)
    verified = models.BooleanField(default=False)

class Requester(UserProfile):

    pass

class UserRoles(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    role = models.ForeignKey(Role)

class Friendship(models.Model):
    user_source = models.ForeignKey(UserProfile, related_name='user_source')
    user_target = models.ForeignKey(UserProfile, related_name='user_target')
    date = models.DateTimeField()
