__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project


class ProjectRequesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectRequester


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Module


class WorkerModuleApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerModuleApplication


class QualificationApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification


class QualificationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QualificationItem
