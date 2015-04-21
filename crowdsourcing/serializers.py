__author__ = 'dmorina'
from rest_framework import serializers
from crowdsourcing import models
from datetime import datetime
import json


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ('id','gender', 'birthday', 'verified','address','nationality','picture','friends','roles','created_on','deleted','languages')