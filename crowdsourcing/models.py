from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone

class RegistrationModel(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    created = models.DateTimeField(default=timezone.now)


class PasswordResetModel(models.Model):
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
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=False)


class Language(models.Model):
    name = models.CharField(max_length=64)
    iso_code = models.CharField(max_length=8)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    gender = models.SmallIntegerField(null=True, error_messages={""})
    address = models.ForeignKey(Address, null=True)
    birthday = models.DateField(null=True)
    nationality = models.ManyToManyField(Country, through='UserCountry')
    verified = models.BooleanField(default=False)
    picture = models.BinaryField(null=True)
    friends = models.ManyToManyField('self', through='Friendship',
                                      symmetrical=False)
    roles = models.ManyToManyField(Role, through='UserRole')
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=False)
    languages = models.ManyToManyField(Language, through='UserLanguage')

class UserCountry(models.Model):
    country = models.ForeignKey(Country)
    user = models.ForeignKey(UserProfile)

class Skill(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=512)
    verified = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True)
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=False)


class Worker(UserProfile):
    skills = models.ManyToManyField(Skill, through='WorkerSkill')


class WorkerSkill(models.Model):
    worker = models.ForeignKey(Worker)
    skill = models.ForeignKey(Skill)
    level = models.IntegerField(null=True)
    verified = models.BooleanField(default=False)

class Requester(UserProfile):

    pass


class UserRole(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    role = models.ForeignKey(Role)


class Friendship(models.Model):
    user_source = models.ForeignKey(UserProfile, related_name='user_source')
    user_target = models.ForeignKey(UserProfile, related_name='user_target')
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=False)

class Category(models.Model):
    name = models.CharField(max_length=128)
    parent = models.ForeignKey('self')
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=False)


class Project(models.Model):
    name = models.CharField(max_length=128)
    collaborators = models.ManyToManyField(Requester, through='ProjectRequester')
    deadline = models.DateTimeField(default=timezone.now())
    keywords = models.TextField()
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, through='ProjectCategory')



class ProjectRequester(models.Model):
    """
        Tracks the list of requesters that collaborate on a specific project
    """
    requester = models.ForeignKey(Requester)
    project = models.ForeignKey(Project)


class Module(models.Model):
    """
        This is a group of similar tasks of the same kind.
        Fields
            -repetition: number of times a task needs to be performed
    """
    name = models.CharField(max_length=128)
    description = models.TextField()
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
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=False)



class ModuleCategory(models.Model):
    module = models.ForeignKey(Module)
    category = models.ForeignKey(Category)


class ProjectCategory(models.Model):
    project = models.ForeignKey(Project)
    category = models.ForeignKey(Category)


class Template(models.Model):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey(Requester)
    source_html = models.TextField()
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=False)


class TemplateItem(models.Model):
    name = models.CharField(max_length=128)
    template = models.ForeignKey(Template)
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=False)


class TemplateItemProperties(models.Model):
    template_item = models.ForeignKey(TemplateItem)
    attribute = models.CharField(max_length=128)
    operator = models.CharField(max_length=128)
    value1 = models.CharField(max_length=128)
    value2 = models.CharField(max_length=128)


class Task(models.Model):
    module = models.ForeignKey(Module)
    #TODO: To be refined
    statuses = ((1, "Created"),
                (2, 'Accepted'),
                (3, 'Reviewed'),
                (4, 'Finished')
    )
    status = models.IntegerField(choices=statuses, default=1)
    created_on = models.DateTimeField(default=timezone.now())
    deleted = models.BooleanField(default=False)


class TaskWorker(models.Model):
    task = models.ForeignKey(Task)
    worker = models.ForeignKey(Worker)
    created_on = models.DateTimeField(default=timezone.now())


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


class WorkerModuleApplication(models.Model):
    worker = models.ForeignKey(Worker)
    module = models.ForeignKey(Module)
    #TODO: To be refined
    statuses = ((1, "Created"),
                (2, 'Accepted'),
                (3, 'Rejected')
    )
    status = models.IntegerField(choices=statuses, default=1)



class ActivityLog(models.Model):

    """
        Track all user's activities: Create, Update and Delete
    """
    activity = models.CharField(max_length=512)
    author = models.ForeignKey(User)
    created_on = models.DateTimeField(default=timezone.now())


class Qualification(models.Model):
    module = models.ForeignKey(Module)
    #TODO: To be refined
    types = ((1, "Strict"),
            (2, 'Flexible'))
    type = models.IntegerField(choices=types, default=1)


class QualificationItem(models.Model):
    qualification = models.ForeignKey(Qualification)
    attribute = models.CharField(max_length=128)
    operator = models.CharField(max_length=128)
    value1 = models.CharField(max_length=128)
    value2 = models.CharField(max_length=128)


class UserLanguage(models.Model):
    language = models.ForeignKey(Language)
    user = models.ForeignKey(UserProfile)


class Currency(models.Model):
    name = models.CharField(max_length=32)
    iso_code = models.CharField(max_length=8)


class UserPreferences(models.Model):
    user = models.OneToOneField(User)
    language = models.ForeignKey(Language)
    currency = models.ForeignKey(Currency)
    login_alerts = models.SmallIntegerField(default=0)
