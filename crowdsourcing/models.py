from django.contrib.auth.models import User
from django.db import models
from oauth2client.django_orm import FlowField, CredentialsField
import pandas as pd
import os
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField, JSONField

from crowdsourcing.utils import get_delimiter


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
    name = models.CharField(max_length=32, unique=True,
                            error_messages={'required': 'Please specify the role name!',
                                            'unique': 'The role %(value)r already exists. Please provide another name!'
                                            })
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
    MALE = 'M'
    FEMALE = 'F'
    GENDER = (
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    user = models.OneToOneField(User)

    gender = models.CharField(max_length=1, choices=GENDER)

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

    last_active = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)


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
    scope = models.CharField(max_length=32, default='daemo')


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


class Template(models.Model):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the template name!"})
    owner = models.ForeignKey(UserProfile)
    source_html = models.TextField(default=None, null=True)
    price = models.FloatField(default=0)
    share_with_others = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class BatchFile(models.Model):
    file = models.FileField(upload_to='project_files/')
    name = models.CharField(max_length=256)
    deleted = models.BooleanField(default=False)
    format = models.CharField(max_length=8, default='csv')
    number_of_rows = models.IntegerField(default=1, null=True)
    column_headers = ArrayField(models.CharField(max_length=64))
    first_row = JSONField(null=True, blank=True)
    hash_sha512 = models.CharField(max_length=128, null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def parse_csv(self):
        delimiter = get_delimiter(self.file.name)
        df = pd.DataFrame(pd.read_csv(self.file, sep=delimiter))
        df = df.where((pd.notnull(df)), None)
        return df.to_dict(orient='records')

    def delete(self, *args, **kwargs):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, self.file.url[1:])
        os.remove(path)
        super(BatchFile, self).delete(*args, **kwargs)


class Project(models.Model):
    STATUS_SAVED = 1
    STATUS_PUBLISHED = 2
    STATUS_IN_PROGRESS = 3
    STATUS_COMPLETED = 4
    STATUS_PAUSED = 5

    PERMISSION_ORW_WRW = 1
    PERMISSION_OR_WRW = 2
    PERMISSION_OR_WR = 3
    PERMISSION_WR = 4

    name = models.CharField(max_length=128, default="Untitled Project",
                            error_messages={'required': "Please enter the project name!"})
    description = models.TextField(null=True, max_length=2048, blank=True)
    owner = models.ForeignKey(Requester, related_name='project_owner')
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    templates = models.ManyToManyField(Template, through='ProjectTemplate')
    categories = models.ManyToManyField(Category, through='ProjectCategory')
    keywords = models.TextField(null=True, blank=True)
    STATUS = (
        (STATUS_SAVED, 'Saved'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_PAUSED, 'Paused')
    )
    status = models.IntegerField(choices=STATUS, default=STATUS_SAVED)
    price = models.FloatField(null=True, blank=True)
    repetition = models.IntegerField(default=1)
    timeout = models.IntegerField(null=True, blank=True)
    deadline = models.DateTimeField(null=True)
    has_data_set = models.BooleanField(default=False)
    data_set_location = models.CharField(max_length=256, null=True, blank=True)
    task_time = models.FloatField(null=True, blank=True)  # in minutes
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    published_time = models.DateTimeField(null=True)
    is_micro = models.BooleanField(default=True)
    is_prototype = models.BooleanField(default=True)
    min_rating = models.FloatField(default=0)
    allow_feedback = models.BooleanField(default=True)
    PERMISSION = (
        (PERMISSION_ORW_WRW, 'Others:Read+Write::Workers:Read+Write'),
        (PERMISSION_OR_WRW, 'Others:Read::Workers:Read+Write'),
        (PERMISSION_OR_WR, 'Others:Read::Workers:Read'),
        (PERMISSION_WR, 'Others:None::Workers:Read')
    )
    feedback_permissions = models.IntegerField(choices=PERMISSION, default=PERMISSION_ORW_WRW)
    batch_files = models.ManyToManyField(BatchFile, through='ProjectBatchFile')
    post_mturk = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.validate_null()
        super(Project, self).save()

    def validate_null(self):
        if self.status == self.STATUS_IN_PROGRESS and (not self.price or not self.repetition):
            raise ValidationError(_('Fields price and repetition are required!'), code='required')


class ProjectCategory(models.Model):
    project = models.ForeignKey(Project)
    category = models.ForeignKey(Category)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        unique_together = ('category', 'project')


class TemplateItem(models.Model):
    ROLE_DISPLAY = 'display'
    ROLE_INPUT = 'input'

    ROLE = (
        (ROLE_DISPLAY, 'Display'),
        (ROLE_INPUT, 'Input'),
    )
    name = models.CharField(max_length=128, default='')
    template = models.ForeignKey(Template, related_name='template_items', on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE, default=ROLE_DISPLAY)
    type = models.CharField(max_length=16)
    sub_type = models.CharField(max_length=16, null=True)
    position = models.IntegerField()
    required = models.BooleanField(default=True)
    aux_attributes = JSONField()
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['position']


class ProjectTemplate(models.Model):
    project = models.ForeignKey(Project, related_name='project_template', on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('project', 'template',)


class TemplateItemProperties(models.Model):
    template_item = models.ForeignKey(TemplateItem)
    attribute = models.CharField(max_length=128)
    operator = models.CharField(max_length=128)
    value1 = models.CharField(max_length=128)
    value2 = models.CharField(max_length=128)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Task(models.Model):
    STATUS_CREATED = 1
    STATUS_ACCEPTED = 2
    STATUS_ASSIGNED = 3
    STATUS_FINISHED = 4

    project = models.ForeignKey(Project, related_name='project_tasks', on_delete=models.CASCADE)

    STATUS = (
        (STATUS_CREATED, "Created"),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_FINISHED, 'Finished')
    )
    status = models.IntegerField(choices=STATUS, default=STATUS_CREATED)
    data = JSONField(null=True)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    price = models.FloatField(default=0)


class TaskWorker(models.Model):
    STATUS_IN_PROGRESS = 1
    STATUS_SUBMITTED = 2
    STATUS_ACCEPTED = 3
    STATUS_REJECTED = 4
    STATUS_RETURNED = 5
    STATUS_SKIPPED = 6

    task = models.ForeignKey(Task, related_name='task_workers', on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker)
    STATUS = (
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_RETURNED, 'Returned'),
        (STATUS_SKIPPED, 'Skipped')
    )
    task_status = models.IntegerField(choices=STATUS, default=STATUS_IN_PROGRESS)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'worker',)


class TaskWorkerResult(models.Model):
    STATUS_CREATED = 1
    STATUS_ACCEPTED = 2
    STATUS_REJECTED = 3

    task_worker = models.ForeignKey(TaskWorker, related_name='task_worker_results', on_delete=models.CASCADE)
    result = JSONField(null=True)
    template_item = models.ForeignKey(TemplateItem)

    STATUS = (
        (STATUS_CREATED, 'Created'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected')
    )
    status = models.IntegerField(choices=STATUS, default=STATUS_CREATED)
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
    TYPE_STRICT = 1
    TYPE_FLEXIBLE = 2

    project = models.ForeignKey(Project)

    TYPE = (
        (TYPE_STRICT, "Strict"),
        (TYPE_FLEXIBLE, 'Flexible')
    )
    type = models.IntegerField(choices=TYPE, default=TYPE_STRICT)
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
    language = models.ForeignKey(Language, null=True, blank=True)
    currency = models.ForeignKey(Currency, null=True, blank=True)
    login_alerts = models.SmallIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    auto_accept = models.BooleanField(default=False)


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


class Conversation(models.Model):
    subject = models.CharField(max_length=64)
    sender = models.ForeignKey(User, related_name='sender')
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    deleted = models.BooleanField(default=False)
    recipients = models.ManyToManyField(User, through='ConversationRecipient')


class Message(models.Model):
    STATUS_SENT = 1
    STATUS_DELIVERED = 2
    STATUS_READ = 3

    STATUS = (
        (STATUS_SENT, "Sent"),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_READ, 'Read')
    )
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User)
    body = models.TextField(max_length=8192)
    deleted = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS, default=STATUS_SENT)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class ConversationRecipient(models.Model):
    STATUS_OPEN = 1
    STATUS_MINIMIZED = 2
    STATUS_CLOSED = 3
    STATUS_MUTED = 4

    STATUS = (
        (STATUS_OPEN, "Open"),
        (STATUS_MINIMIZED, 'Minimized'),
        (STATUS_CLOSED, 'Closed'),
        (STATUS_MUTED, 'Muted')
    )
    recipient = models.ForeignKey(User, related_name='recipients')
    conversation = models.ForeignKey(Conversation, related_name='conversations', on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=STATUS, default=STATUS_OPEN)
    date_added = models.DateTimeField(auto_now_add=True, auto_now=False)
    deleted = models.BooleanField(default=False)


class UserMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(User)
    deleted = models.BooleanField(default=False)


class ProjectBatchFile(models.Model):
    batch_file = models.ForeignKey(BatchFile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('batch_file', 'project',)


class WorkerRequesterRating(models.Model):
    origin = models.ForeignKey(UserProfile, related_name='rating_origin')
    target = models.ForeignKey(UserProfile, related_name='rating_target')
    weight = models.FloatField(default=2)
    origin_type = models.CharField(max_length=16)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        index_together = [
            ['origin', 'target'],
            ['origin', 'target', 'last_updated', 'origin_type']
        ]


class Comment(models.Model):
    sender = models.ForeignKey(UserProfile, related_name='comment_sender')
    body = models.TextField(max_length=8192)
    parent = models.ForeignKey('self', related_name='reply_to', null=True)
    deleted = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        ordering = ['created_timestamp']


class ProjectComment(models.Model):
    project = models.ForeignKey(Project, related_name='projectcomment_project')
    comment = models.ForeignKey(Comment, related_name='projectcomment_comment')
    deleted = models.BooleanField(default=False)


class TaskComment(models.Model):
    task = models.ForeignKey(Task, related_name='taskcomment_task')
    comment = models.ForeignKey(Comment, related_name='taskcomment_comment')
    deleted = models.BooleanField(default=False)


class FinancialAccount(models.Model):
    owner = models.ForeignKey(UserProfile, related_name='financial_accounts', null=True)
    type = models.CharField(max_length=16, default='general')
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(default=0, decimal_places=4, max_digits=19)
    is_system = models.BooleanField(default=False)


class PayPalFlow(models.Model):
    paypal_id = models.CharField(max_length=128)
    state = models.CharField(max_length=16, default='created')
    recipient = models.ForeignKey(FinancialAccount, related_name='flows_received')
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    redirect_url = models.CharField(max_length=256)
    payer_id = models.CharField(max_length=64, null=True)


class Transaction(models.Model):
    sender = models.ForeignKey(FinancialAccount, related_name='transactions_sent')
    recipient = models.ForeignKey(FinancialAccount, related_name='transactions_received')
    currency = models.CharField(max_length=4, default='USD')
    amount = models.DecimalField(decimal_places=4, max_digits=19)
    method = models.CharField(max_length=16, default='paypal')
    state = models.CharField(max_length=16, default='created')
    sender_type = models.CharField(max_length=8, default='self')
    reference = models.CharField(max_length=256, null=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
