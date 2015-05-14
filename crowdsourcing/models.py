from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core import validators
from django.core.exceptions import ValidationError


class RegistrationModel(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class PasswordResetModel(models.Model):
    user = models.OneToOneField(User)
    reset_key = models.CharField(max_length=40)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Region(models.Model):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the region!', })
    code = models.CharField(max_length=16, error_messages={'required': 'Please specify the region code!', })
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

class Country(models.Model):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the country!', })
    code = models.CharField(max_length=8, error_messages={'required': 'Please specify the country code!', })
    region = models.ForeignKey(Region)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

class City(models.Model):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the city!', })
    country = models.ForeignKey(Country)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

class Address(models.Model):
    street = models.CharField(max_length=128, error_messages={'required': 'Please specify the street name!', })
    country = models.ForeignKey(Country)
    city = models.ForeignKey(City)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

class Role(models.Model):
    name = models.CharField(max_length=32, unique=True, error_messages={'required': 'Please specify the role name!', 'unique': 'The role %(value)r already exists. Please provide another name!'})
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

class Language(models.Model):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the language!'})
    iso_code = models.CharField(max_length=8)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    gender_choices = (('M', 'Male'),('F', 'Female'))
    gender = models.CharField(max_length=1, choices=gender_choices)

    address = models.ForeignKey(Address, null=True)
    birthday = models.DateField(null=True, error_messages={'invalid': "Please enter a correct date format"})

    nationality = models.ManyToManyField(Country, through='UserCountry')
    verified = models.BooleanField(default=False)
    picture = models.BinaryField(null=True)
    friends = models.ManyToManyField('self', through='Friendship',
                                      symmetrical=False)
    roles = models.ManyToManyField(Role, through='UserRole')
    deleted = models.BooleanField(default=False)
    languages = models.ManyToManyField(Language, through='UserLanguage')
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class UserCountry(models.Model):
    country = models.ForeignKey(Country)
    user = models.ForeignKey(UserProfile)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Skill(models.Model):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the skill name!"})
    description = models.CharField(max_length=512, error_messages={'required': "Please enter the skill description!"})
    verified = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Worker(models.Model):
    profile = models.OneToOneField(UserProfile)
    skills = models.ManyToManyField(Skill, through='WorkerSkill')


class WorkerSkill(models.Model):
    worker = models.ForeignKey(Worker)
    skill = models.ForeignKey(Skill)
    level = models.IntegerField(null=True)
    verified = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Requester(models.Model):
    profile = models.OneToOneField(UserProfile)

class UserRole(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    role = models.ForeignKey(Role)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Friendship(models.Model):
    user_source = models.ForeignKey(UserProfile, related_name='user_source')
    user_target = models.ForeignKey(UserProfile, related_name='user_target')
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Category(models.Model):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the category name!"})
    parent = models.ForeignKey('self', null=True)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Project(models.Model):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the project name!"})
    collaborators = models.ManyToManyField(Requester, through='ProjectRequester')
    deadline = models.DateTimeField(default=timezone.now())
    keywords = models.TextField()
    deleted = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, through='ProjectCategory')
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class ProjectRequester(models.Model):
    """
        Tracks the list of requesters that collaborate on a specific project
    """
    requester = models.ForeignKey(Requester)
    project = models.ForeignKey(Project)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Module(models.Model):
    """
        This is a group of similar tasks of the same kind.
        Fields
            -repetition: number of times a task needs to be performed
    """
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the module name!"})
    description = models.TextField(error_messages={'required': "Please enter the module description!"})
    owner = models.ForeignKey(Requester)
    project = models.ForeignKey(Project)
    categories = models.ManyToManyField(Category, through='ModuleCategory')
    keywords = models.TextField()
    #TODO: To be refined
    statuses = ((1, "Created"),
                (2, 'In Progress'),
                (3, 'In Review'),
                (4, 'Finished')
    )
    status = models.IntegerField(choices=statuses, default=1)
    price = models.FloatField()
    repetition = models.IntegerField()
    module_timeout = models.IntegerField()
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class ModuleCategory(models.Model):
    module = models.ForeignKey(Module)
    category = models.ForeignKey(Category)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class ProjectCategory(models.Model):
    project = models.ForeignKey(Project)
    category = models.ForeignKey(Category)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Template(models.Model):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the template name!"})
    owner = models.ForeignKey(Requester)
    source_html = models.TextField()
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class TemplateItem(models.Model):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the name of the template item!"})
    template = models.ForeignKey(Template)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class TemplateItemProperties(models.Model):
    template_item = models.ForeignKey(TemplateItem)
    attribute = models.CharField(max_length=128)
    operator = models.CharField(max_length=128)
    value1 = models.CharField(max_length=128)
    value2 = models.CharField(max_length=128)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Task(models.Model):
    module = models.ForeignKey(Module)
    #TODO: To be refined
    statuses = ((1, "Created"),
                (2, 'Accepted'),
                (3, 'Reviewed'),
                (4, 'Finished')
    )
    status = models.IntegerField(choices=statuses, default=1)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class TaskWorker(models.Model):
    task = models.ForeignKey(Task)
    worker = models.ForeignKey(Worker)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class TaskWorkerResult(models.Model):
    task_worker = models.ForeignKey(TaskWorker)
    template_item = models.ForeignKey(TemplateItem)
    #TODO: To be refined
    statuses = ((1, "Created"),
                (2, 'Accepted'),
                (3, 'Reviewed'),
                (4, 'Finished')
    )
    status = models.IntegerField(choices=statuses, default=1)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class WorkerModuleApplication(models.Model):
    worker = models.ForeignKey(Worker)
    module = models.ForeignKey(Module)
    #TODO: To be refined
    statuses = ((1, "Created"),
                (2, 'Accepted'),
                (3, 'Rejected')
    )
    status = models.IntegerField(choices=statuses, default=1)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class ActivityLog(models.Model):

    """
        Track all user's activities: Create, Update and Delete
    """
    activity = models.CharField(max_length=512)
    author = models.ForeignKey(User)
    created_timestamp = models.DateTimeField(auto_now_add=False, auto_now=True)


class Qualification(models.Model):
    module = models.ForeignKey(Module)
    #TODO: To be refined
    types = ((1, "Strict"),
            (2, 'Flexible'))
    type = models.IntegerField(choices=types, default=1)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class QualificationItem(models.Model):
    qualification = models.ForeignKey(Qualification)
    attribute = models.CharField(max_length=128)
    operator = models.CharField(max_length=128)
    value1 = models.CharField(max_length=128)
    value2 = models.CharField(max_length=128)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

class UserLanguage(models.Model):
    language = models.ForeignKey(Language)
    user = models.ForeignKey(UserProfile)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Currency(models.Model):
    name = models.CharField(max_length=32)
    iso_code = models.CharField(max_length=8)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

class UserPreferences(models.Model):
    user = models.OneToOneField(User)
    language = models.ForeignKey(Language)
    currency = models.ForeignKey(Currency)
    login_alerts = models.SmallIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    
class RequesterRanking(models.Model):   
    requester_name = models.CharField(max_length=128)
    requester_payRank = models.FloatField()  
    requester_fairRank = models.FloatField()
    requester_speedRank = models.FloatField()
    requester_communicationRank = models.FloatField()
    requester_numberofReviews = models.IntegerField(default=0) 
