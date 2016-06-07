import os
from datetime import datetime

import pandas as pd
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from oauth2client.django_orm import FlowField, CredentialsField

from crowdsourcing.utils import get_delimiter


class TimeStampable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True


class ArchiveQuerySet(models.query.QuerySet):
    def delete(self):
        self.archive()

    def archive(self):
        deleted_at = datetime.timezone.now()
        self.update(deleted_at=deleted_at)

    def active(self):
        return self.filter(deleted_at__isnull=True)


class ArchiveManager(models.Manager):
    def get_queryset(self):
        return ArchiveQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()


class Archivable(models.Model):
    deleted_at = models.DateTimeField(null=True)

    objects = ArchiveManager()

    class Meta:
        abstract = True


class Activable(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Verifiable(models.Model):
    is_verified = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Revisable(models.Model):
    revised_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    revision_log = models.CharField(max_length=512, null=True, blank=True)
    group_id = models.IntegerField(null=True)

    class Meta:
        abstract = True


class Region(TimeStampable):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the region!'})
    code = models.CharField(max_length=16, error_messages={'required': 'Please specify the region code!'})


class Country(TimeStampable):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the country!'})
    code = models.CharField(max_length=8, error_messages={'required': 'Please specify the country code!'})
    region = models.ForeignKey(Region, related_name='countries')

    def __unicode__(self):
        return u'%s' % (self.name,)


class City(TimeStampable):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the city!'})
    country = models.ForeignKey(Country, related_name='cities')

    def __unicode__(self):
        return u'%s' % (self.name,)


class Address(TimeStampable):
    street = models.CharField(max_length=128, error_messages={'required': 'Please specify the street name!'})
    city = models.ForeignKey(City, related_name='addresses', null=True, blank=True)

    def __unicode__(self):
        return u'%s, %s, %s' % (self.street, self.city.name, self.city.country.name)


class Language(TimeStampable):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the language!'})
    iso_code = models.CharField(max_length=8)


class Skill(TimeStampable, Archivable, Verifiable):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the skill name!"})
    description = models.CharField(max_length=512, error_messages={'required': "Please enter the skill description!"})
    parent = models.ForeignKey('self', related_name='skills', null=True)


class Role(TimeStampable, Archivable, Activable):
    name = models.CharField(max_length=32, unique=True,
                            error_messages={'required': 'Please specify the role name!',
                                            'unique': 'The role %(value)r already exists. Please provide another name!'
                                            })


class Currency(TimeStampable):
    name = models.CharField(max_length=32)
    iso_code = models.CharField(max_length=8)


class Category(TimeStampable, Archivable):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the category name!"})
    parent = models.ForeignKey('self', related_name='categories', null=True)


class UserRegistration(TimeStampable):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)


class UserPasswordReset(TimeStampable):
    user = models.OneToOneField(User)
    reset_key = models.CharField(max_length=40)


class UserProfile(TimeStampable, Archivable, Verifiable):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'

    GENDER = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other')
    )

    ETHNICITY = (
        ('white', 'White'),
        ('hispanic', 'Hispanic'),
        ('black', 'Black'),
        ('islander', 'Native Hawaiian or Other Pacific Islander'),
        ('indian', 'Indian'),
        ('asian', 'Asian'),
        ('native', 'Native American or Alaska Native')
    )

    user = models.OneToOneField(User, related_name='profile')
    gender = models.CharField(max_length=1, choices=GENDER, blank=True)
    ethnicity = models.CharField(max_length=8, choices=ETHNICITY, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    address = models.ForeignKey(Address, related_name='+', blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True)
    nationality = models.ManyToManyField(Country, through='UserCountry')
    languages = models.ManyToManyField(Language, through='UserLanguage')
    picture = models.BinaryField(null=True)
    last_active = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    is_worker = models.BooleanField(default=True)
    is_requester = models.BooleanField(default=False)


class UserCountry(TimeStampable):
    country = models.ForeignKey(Country)
    user = models.ForeignKey(UserProfile)


class UserSkill(TimeStampable, Verifiable):
    user = models.ForeignKey(User)
    skill = models.ForeignKey(Skill)
    level = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'skill')


class UserRole(TimeStampable):
    user = models.ForeignKey(User)
    role = models.ForeignKey(Role)


class UserLanguage(TimeStampable):
    language = models.ForeignKey(Language)
    user = models.ForeignKey(UserProfile)


class UserPreferences(TimeStampable):
    user = models.OneToOneField(User)
    language = models.ForeignKey(Language, null=True, blank=True)
    currency = models.ForeignKey(Currency, null=True, blank=True)
    login_alerts = models.SmallIntegerField(default=0)
    auto_accept = models.BooleanField(default=False)


class Friendship(TimeStampable, Archivable):
    origin = models.ForeignKey(User, related_name='friends_to')
    target = models.ForeignKey(User, related_name='friends_from')


class Template(TimeStampable, Archivable, Revisable):
    name = models.CharField(max_length=128, error_messages={'required': "Please enter the template name!"})
    owner = models.ForeignKey(User, related_name='templates')
    source_html = models.TextField(default=None, null=True)
    price = models.FloatField(default=0)
    share_with_others = models.BooleanField(default=False)


class BatchFile(TimeStampable, Archivable):
    name = models.CharField(max_length=256)
    file = models.FileField(upload_to='project_files/')
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


class Project(TimeStampable, Archivable, Revisable):
    STATUS_DRAFT = 1
    STATUS_PUBLISHED = 2
    STATUS_IN_PROGRESS = 3
    STATUS_COMPLETED = 4
    STATUS_PAUSED = 5

    STATUS = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_PAUSED, 'Paused')
    )

    PERMISSION_ORW_WRW = 1
    PERMISSION_OR_WRW = 2
    PERMISSION_OR_WR = 3
    PERMISSION_WR = 4

    PERMISSION = (
        (PERMISSION_ORW_WRW, 'Others:Read+Write::Workers:Read+Write'),
        (PERMISSION_OR_WRW, 'Others:Read::Workers:Read+Write'),
        (PERMISSION_OR_WR, 'Others:Read::Workers:Read'),
        (PERMISSION_WR, 'Others:None::Workers:Read')
    )

    name = models.CharField(max_length=128, default="Untitled Project",
                            error_messages={'required': "Please enter the project name!"})
    description = models.TextField(null=True, max_length=2048, blank=True)
    owner = models.ForeignKey(User, related_name='projects')
    parent = models.ForeignKey('self', related_name='projects', null=True, on_delete=models.CASCADE)
    templates = models.ManyToManyField(Template, through='ProjectTemplate')
    categories = models.ManyToManyField(Category, through='ProjectCategory')
    keywords = models.TextField(null=True, blank=True)

    status = models.IntegerField(choices=STATUS, default=STATUS_DRAFT)
    price = models.FloatField(null=True, blank=True)
    repetition = models.IntegerField(default=1)
    timeout = models.IntegerField(null=True, blank=True)
    deadline = models.DateTimeField(null=True)
    has_data_set = models.BooleanField(default=False)
    data_set_location = models.CharField(max_length=256, null=True, blank=True)
    task_time = models.FloatField(null=True, blank=True)  # in minutes
    published_at = models.DateTimeField(null=True)
    is_micro = models.BooleanField(default=True)
    is_prototype = models.BooleanField(default=True)
    min_rating = models.FloatField(default=0)
    allow_feedback = models.BooleanField(default=True)
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


class ProjectBatchFile(models.Model):
    batch_file = models.ForeignKey(BatchFile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('batch_file', 'project',)


class ProjectCategory(TimeStampable):
    project = models.ForeignKey(Project)
    category = models.ForeignKey(Category)

    class Meta:
        unique_together = ('category', 'project')


class ProjectTemplate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('project', 'template',)


class TemplateItem(TimeStampable, Archivable, Revisable):
    ROLE_DISPLAY = 'display'
    ROLE_INPUT = 'input'

    ROLE = (
        (ROLE_DISPLAY, 'Display'),
        (ROLE_INPUT, 'Input'),
    )
    name = models.CharField(max_length=128, default='')
    template = models.ForeignKey(Template, related_name='items', on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE, default=ROLE_DISPLAY)
    type = models.CharField(max_length=16)
    sub_type = models.CharField(max_length=16, null=True)
    position = models.IntegerField()
    required = models.BooleanField(default=True)
    aux_attributes = JSONField()

    class Meta:
        ordering = ['position']


class TemplateItemProperties(TimeStampable):
    template_item = models.ForeignKey(TemplateItem, related_name='properties')
    attribute = models.CharField(max_length=128)
    operator = models.CharField(max_length=128)
    value1 = models.CharField(max_length=128)
    value2 = models.CharField(max_length=128)


class Task(TimeStampable, Archivable, Revisable):
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    data = JSONField(null=True)


class TaskWorker(TimeStampable, Archivable, Revisable):
    STATUS_IN_PROGRESS = 1
    STATUS_SUBMITTED = 2
    STATUS_ACCEPTED = 3
    STATUS_REJECTED = 4
    STATUS_RETURNED = 5
    STATUS_SKIPPED = 6
    STATUS_EXPIRED = 7

    STATUS = (
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_RETURNED, 'Returned'),
        (STATUS_SKIPPED, 'Skipped'),
        (STATUS_EXPIRED, 'Expired'),
    )

    task = models.ForeignKey(Task, related_name='task_workers', on_delete=models.CASCADE)
    worker = models.ForeignKey(User, related_name='task_workers')
    status = models.IntegerField(choices=STATUS, default=STATUS_IN_PROGRESS)
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'worker')


class TaskWorkerResult(TimeStampable, Archivable):
    task_worker = models.ForeignKey(TaskWorker, related_name='results', on_delete=models.CASCADE)
    result = JSONField(null=True)
    template_item = models.ForeignKey(TemplateItem, related_name='+')


class ActivityLog(TimeStampable):
    """
        Track all user's activities: Create, Update and Delete
    """
    activity = models.CharField(max_length=512)
    author = models.ForeignKey(User, related_name='activities')


class Qualification(TimeStampable):
    TYPE_STRICT = 1
    TYPE_FLEXIBLE = 2

    TYPE = (
        (TYPE_STRICT, "Strict"),
        (TYPE_FLEXIBLE, 'Flexible')
    )

    project = models.ForeignKey(Project, related_name='qualifications')
    type = models.IntegerField(choices=TYPE, default=TYPE_STRICT)


class QualificationItem(TimeStampable):
    qualification = models.ForeignKey(Qualification, related_name='items')
    attribute = models.CharField(max_length=128)
    operator = models.CharField(max_length=128)
    value1 = models.CharField(max_length=128)
    value2 = models.CharField(max_length=128)


class Rating(TimeStampable):
    RATING_WORKER = 1
    RATING_REQUESTER = 2

    RATING = (
        (RATING_WORKER, "Worker"),
        (RATING_REQUESTER, 'Requester')
    )

    origin = models.ForeignKey(User, related_name='ratings_to')
    target = models.ForeignKey(User, related_name='ratings_from')
    weight = models.FloatField(default=2)
    origin_type = models.IntegerField(choices=RATING)

    class Meta:
        index_together = [
            ['origin', 'target'],
            ['origin', 'target', 'updated_at', 'origin_type']
        ]


class Conversation(TimeStampable, Archivable):
    subject = models.CharField(max_length=64)
    sender = models.ForeignKey(User, related_name='conversations')
    recipients = models.ManyToManyField(User, through='ConversationRecipient')


class Message(TimeStampable, Archivable):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages')
    body = models.TextField(max_length=8192)
    recipients = models.ManyToManyField(User, through='MessageRecipient')


class ConversationRecipient(TimeStampable, Archivable):
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
    recipient = models.ForeignKey(User)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=STATUS, default=STATUS_OPEN)


class MessageRecipient(Archivable):
    STATUS_SENT = 1
    STATUS_DELIVERED = 2
    STATUS_READ = 3

    STATUS = (
        (STATUS_SENT, "Sent"),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_READ, 'Read')
    )

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS, default=STATUS_SENT)


class Comment(TimeStampable, Archivable):
    sender = models.ForeignKey(User, related_name='comments')
    body = models.TextField(max_length=8192)
    parent = models.ForeignKey('self', related_name='comments', null=True)

    class Meta:
        ordering = ['created_at']


class ProjectComment(TimeStampable, Archivable):
    project = models.ForeignKey(Project, related_name='comments')
    comment = models.ForeignKey(Comment)


class TaskComment(TimeStampable, Archivable):
    task = models.ForeignKey(Task, related_name='comments')
    comment = models.ForeignKey(Comment)


class FinancialAccount(TimeStampable, Activable):
    TYPE_WORKER = 1
    TYPE_REQUESTER = 2

    TYPE = (
        (TYPE_WORKER, "Worker"),
        (TYPE_REQUESTER, 'Requester')
    )
    owner = models.ForeignKey(User, related_name='financial_accounts', null=True)
    type = models.IntegerField(choices=TYPE)
    balance = models.DecimalField(default=0, decimal_places=4, max_digits=19)
    is_system = models.BooleanField(default=False)


class GoogleAuth(models.Model):
    id = models.OneToOneField(User, primary_key=True)
    flow = FlowField()


class DropboxAuth(models.Model):
    user = models.ForeignKey(User)
    type = models.CharField(max_length=16)
    email = models.EmailField()


class ExternalAccount(Activable):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=16)
    email = models.EmailField()
    access_token = models.TextField(max_length=2048)
    root = models.CharField(max_length=256)
    quota = models.BigIntegerField()
    used_space = models.BigIntegerField()
    assigned_space = models.BigIntegerField()
    owner = models.ForeignKey(User, related_name='external_accounts')


class GoogleCredential(models.Model):
    account = models.ForeignKey(ExternalAccount)
    credential = CredentialsField()


class PayPalFlow(TimeStampable):
    paypal_id = models.CharField(max_length=128)
    state = models.CharField(max_length=16, default='created')
    recipient = models.ForeignKey(FinancialAccount, related_name='flows_received')
    redirect_url = models.CharField(max_length=256)
    payer_id = models.CharField(max_length=64, null=True)


class Transaction(TimeStampable):
    sender = models.ForeignKey(FinancialAccount, related_name='transactions_sent')
    recipient = models.ForeignKey(FinancialAccount, related_name='transactions_received')
    currency = models.CharField(max_length=4, default='USD')
    amount = models.DecimalField(decimal_places=4, max_digits=19)
    method = models.CharField(max_length=16, default='paypal')
    state = models.CharField(max_length=16, default='created')
    sender_type = models.CharField(max_length=8, default='self')
    reference = models.CharField(max_length=256, null=True)
