from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from oauth2client.django_orm import FlowField, CredentialsField
from crowdsourcing.utils import get_delimiter
import pandas as pd
import os


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

    def __unicode__(self):
        return u'%s' % (self.name)


class City(models.Model):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the city!', })
    country = models.ForeignKey(Country)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return u'%s' % (self.name)


class Address(models.Model):
    street = models.CharField(max_length=128, error_messages={'required': 'Please specify the street name!', })
    country = models.ForeignKey(Country)
    city = models.ForeignKey(City)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return u'%s, %s, %s' % (self.street, self.city, self.country)


class Role(models.Model):
    name = models.CharField(max_length=32, unique=True, error_messages={'required': 'Please specify the role name!',
                                                                        'unique': 'The role %(value)r already exists. Please provide another name!'})
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

    gender_choices = (('M', 'Male'), ('F', 'Female'))
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
    deleted = models.BooleanField(default=False)
    alias = models.CharField(max_length=32, error_messages={'required': "Please enter an alias!"})


class WorkerSkill(models.Model):
    worker = models.ForeignKey(Worker)
    skill = models.ForeignKey(Skill)
    level = models.IntegerField(null=True)
    verified = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        unique_together = ('worker', 'skill')


class Requester(models.Model):
    profile = models.OneToOneField(UserProfile)
    alias = models.CharField(max_length=32, error_messages={'required': "Please enter an alias!"})


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
    start_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    end_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    owner = models.ForeignKey(Requester, related_name='project_owner')
    description = models.CharField(max_length=1024, default='')
    collaborators = models.ManyToManyField(Requester, through='ProjectRequester')
    keywords = models.TextField(null=True)
    save_to_drive = models.BooleanField(default=False)
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

    class Meta:
        unique_together = ('requester', 'project')


class Template(models.Model):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the template name!"})
    owner = models.ForeignKey(UserProfile)
    source_html = models.TextField(default=None, null=True)
    price = models.FloatField(default=0)
    share_with_others = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Module(models.Model):
    """
        aka Milestone
        This is a group of similar tasks of the same kind.
        Fields
            -repetition: number of times a task needs to be performed
    """
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the module name!"})
    description = models.TextField(error_messages={'required': "Please enter the module description!"}, max_length=2048)
    owner = models.ForeignKey(Requester)
    project = models.ForeignKey(Project, related_name='modules')
    categories = models.ManyToManyField(Category, through='ModuleCategory')
    keywords = models.TextField(null=True)
    # TODO: To be refined
    statuses = ((1, "Created"),
                (2, 'In Review'),
                (3, 'In Progress'),
                (4, 'Completed'),
                (5, 'Paused')
                )
    permission_types = ((1, "Others:Read+Write::Workers:Read+Write"),
                        (2, 'Others:Read::Workers:Read+Write'),
                        (3, 'Others:Read::Workers:Read'),
                        (4, 'Others:None::Workers:Read')
                        )
    status = models.IntegerField(choices=statuses, default=1)
    price = models.FloatField()
    repetition = models.IntegerField(default=1)
    module_timeout = models.IntegerField(default=0)
    has_data_set = models.BooleanField(default=False)
    data_set_location = models.CharField(max_length=256, default='No data set', null=True)
    task_time = models.FloatField(default=0)  # in minutes
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    template = models.ManyToManyField(Template, through='ModuleTemplate')
    is_micro = models.BooleanField(default=True)
    is_prototype = models.BooleanField(default=False)
    min_rating = models.FloatField(default=0)
    allow_feedback = models.BooleanField(default=True)
    feedback_permissions = models.IntegerField(choices=permission_types, default=1)


class ModuleCategory(models.Model):
    module = models.ForeignKey(Module)
    category = models.ForeignKey(Category)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        unique_together = ('category', 'module')


class ProjectCategory(models.Model):
    project = models.ForeignKey(Project)
    category = models.ForeignKey(Category)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        unique_together = ('project', 'category')


class TemplateItem(models.Model):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the name of the template item!"})
    template = models.ForeignKey(Template, related_name='template_items')
    id_string = models.CharField(max_length=128)
    role = models.CharField(max_length=16)
    icon = models.CharField(max_length=256, null=True)
    data_source = models.CharField(max_length=256, null=True)
    layout = models.CharField(max_length=16, default='column')
    type = models.CharField(max_length=16)
    sub_type = models.CharField(max_length=16)
    values = models.TextField(null=True)
    position = models.IntegerField()
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['position']


class ModuleTemplate(models.Model):
    module = models.ForeignKey(Module)
    template = models.ForeignKey(Template)


class TemplateItemProperties(models.Model):
    template_item = models.ForeignKey(TemplateItem)
    attribute = models.CharField(max_length=128)
    operator = models.CharField(max_length=128)
    value1 = models.CharField(max_length=128)
    value2 = models.CharField(max_length=128)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Task(models.Model):
    module = models.ForeignKey(Module, related_name='module_tasks')
    # TODO: To be refined
    statuses = ((1, "Created"),
                (2, 'Accepted'),
                (3, 'Assigned'),
                (4, 'Finished')
                )
    status = models.IntegerField(choices=statuses, default=1)
    data = models.TextField(null=True)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    price = models.FloatField(default=0)


class TaskWorker(models.Model):
    task = models.ForeignKey(Task, related_name='task_workers')
    worker = models.ForeignKey(Worker)
    statuses = ((1, 'In Progress'),
                (2, 'Submitted'),
                (3, 'Accepted'),
                (4, 'Rejected'),
                (5, 'Returned'),
                (6, 'Skipped')
                )
    task_status = models.IntegerField(choices=statuses, default=1)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    is_paid = models.BooleanField(default=False)


class TaskWorkerResult(models.Model):
    task_worker = models.ForeignKey(TaskWorker, related_name='task_worker_results')
    result = models.TextField(null=True)
    template_item = models.ForeignKey(TemplateItem)
    # TODO: To be refined
    statuses = ((1, 'Created'),
                (2, 'Accepted'),
                (3, 'Rejected')
                )
    status = models.IntegerField(choices=statuses, default=1)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class WorkerModuleApplication(models.Model):
    worker = models.ForeignKey(Worker)
    module = models.ForeignKey(Module)
    # TODO: To be refined
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
    # TODO: To be refined
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


class ModuleRating(models.Model):
    worker = models.ForeignKey(Worker)
    module = models.ForeignKey(Module)
    value = models.IntegerField()
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        unique_together = ('worker', 'module')


class ModuleReview(models.Model):
    worker = models.ForeignKey(Worker)
    anonymous = models.BooleanField(default=False)
    module = models.ForeignKey(Module)
    comments = models.TextField()
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        unique_together = ('worker', 'module')


class FlowModel(models.Model):
    id = models.OneToOneField(User, primary_key=True)
    flow = FlowField()


class AccountModel(models.Model):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=16)
    email = models.EmailField()
    access_token = models.TextField(max_length=2048)
    root = models.CharField(max_length=256)
    is_active = models.IntegerField()
    quota = models.BigIntegerField()
    used_space = models.BigIntegerField()
    assigned_space = models.BigIntegerField()
    status = models.IntegerField(default=quota)
    owner = models.ForeignKey(User)


class CredentialsModel(models.Model):
    account = models.ForeignKey(AccountModel)
    credential = CredentialsField()


class TemporaryFlowModel(models.Model):
    user = models.ForeignKey(User)
    type = models.CharField(max_length=16)
    email = models.EmailField()


class BookmarkedProjects(models.Model):
    profile = models.ForeignKey(UserProfile)
    project = models.ForeignKey(Project)


class Conversation(models.Model):
    subject = models.CharField(max_length=64)
    sender = models.ForeignKey(User, related_name='sender')
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    deleted = models.BooleanField(default=False)
    recipients = models.ManyToManyField(User, through='ConversationRecipient')


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages')
    sender = models.ForeignKey(User)
    body = models.TextField(max_length=8192)
    deleted = models.BooleanField(default=False)
    status = models.IntegerField(default=1)  # 1:Sent 2:Delivered 3:Read
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class ConversationRecipient(models.Model):
    recipient = models.ForeignKey(User, related_name='recipients')
    conversation = models.ForeignKey(Conversation, related_name='conversation_recipient')
    date_added = models.DateTimeField(auto_now_add=True, auto_now=False)


class UserMessage(models.Model):
    message = models.ForeignKey(Message)
    user = models.ForeignKey(User)
    deleted = models.BooleanField(default=False)


class RequesterInputFile(models.Model):
    # TODO will need save files on a server rather than in a temporary folder
    file = models.FileField(upload_to='tmp/')
    deleted = models.BooleanField(default=False)

    def parse_csv(self):
        delimiter = get_delimiter(self.file.name)
        df = pd.DataFrame(pd.read_csv(self.file, sep=delimiter))
        return df.to_dict(orient='records')

    def delete(self, *args, **kwargs):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, self.file.url[1:])
        os.remove(path)
        super(RequesterInputFile, self).delete(*args, **kwargs)


class WorkerRequesterRating(models.Model):
    origin = models.ForeignKey(UserProfile, related_name='rating_origin')
    target = models.ForeignKey(UserProfile, related_name='rating_target')
    module = models.ForeignKey(Module, related_name='rating_module')
    weight = models.FloatField(default=2)
    origin_type = models.CharField(max_length=16)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Comment(models.Model):
    sender = models.ForeignKey(UserProfile, related_name='comment_sender')
    body = models.TextField(max_length=8192)
    parent = models.ForeignKey('self', related_name='reply_to', null=True)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['created_timestamp']


class ModuleComment(models.Model):
    module = models.ForeignKey(Module, related_name='modulecomment_module')
    comment = models.ForeignKey(Comment, related_name='modulecomment_comment')
    deleted = models.BooleanField(default=False)


class TaskComment(models.Model):
    task = models.ForeignKey(Task, related_name='taskcomment_task')
    comment = models.ForeignKey(Comment, related_name='taskcomment_comment')
    deleted = models.BooleanField(default=False)


try:
    from crowdsourcing.experimental_models import *
except ImportError as e:
    pass
