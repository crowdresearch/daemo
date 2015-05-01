__author__ = 'elsabakiu'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json


class RequesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Requester


class RequesterRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RequesterRanking
