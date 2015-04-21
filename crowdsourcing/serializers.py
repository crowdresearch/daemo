__author__ = 'dmorina'
from rest_framework import serializers
from crowdsourcing import models
from datetime import datetime
import json


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ('id','gender', 'birthday', 'verified','address','nationality','picture','friends','roles','created_on','deleted','languages')

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.User
		fields = ('id', 'username', 'first_name', 'last_name', 'email',
			'is_superuser', 'is_staff', 'last_login', 'date_joined')