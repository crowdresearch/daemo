import json
import os

import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.utils import timezone

from crowdsourcing.utils import get_delimiter, get_worker_cache


class TimeStampable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True


class StripeObject(models.Model):
    stripe_id = models.CharField(max_length=128, db_index=True)
    stripe_data = JSONField(null=True)

    class Meta:
        abstract = True


class ArchiveQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)

    def inactive(self):
        return self.filter(deleted_at__isnull=False)


class Archivable(models.Model):
    deleted_at = models.DateTimeField(null=True)

    objects = ArchiveQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.archive()

    def archive(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        super(Archivable, self).delete()


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
    group_id = models.IntegerField(null=True, db_index=True)

    class Meta:
        abstract = True


class Region(TimeStampable):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the region!'})
    code = models.CharField(max_length=16, error_messages={'required': 'Please specify the region code!'})


class Country(TimeStampable):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the country!'})
    code = models.CharField(max_length=8, error_messages={'required': 'Please specify the country code!'})
    region = models.ForeignKey(Region, related_name='countries', null=True, blank=True)

    def __unicode__(self):
        return u'%s' % (self.name,)


class City(TimeStampable):
    name = models.CharField(max_length=64, error_messages={'required': 'Please specify the city!'})
    state = models.CharField(max_length=64, blank=True)
    state_code = models.CharField(max_length=64, blank=True)
    country = models.ForeignKey(Country, related_name='cities')

    def __unicode__(self):
        return u'%s' % (self.name,)


class Address(TimeStampable):
    street = models.CharField(max_length=128, blank=True, null=True)
    city = models.ForeignKey(City, related_name='addresses', null=True, blank=True)
    postal_code = models.CharField(null=True, blank=True, max_length=32)

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


class RegistrationWhitelist(TimeStampable):
    email = models.EmailField(db_index=True)
    valid_from = models.DateTimeField(null=True)


class UserPasswordReset(TimeStampable):
    user = models.OneToOneField(User)
    reset_key = models.CharField(max_length=40)


class UserProfile(TimeStampable, Verifiable):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    DO_NOT_STATE = ('DNS', 'Prefer not to specify')

    GENDER = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other')
    )

    PERSONAL = 'personal'
    PROFESSIONAL = 'professional'
    OTHER = 'other'
    RESEARCH = 'research'
    PURPOSE_OF_USE = (
        (PROFESSIONAL, 'Professional'),
        (PERSONAL, 'personal'),
        (RESEARCH, 'research'),
        (OTHER, 'other')
    )

    ETHNICITY = (
        ('white', 'White'),
        ('hispanic', 'Hispanic'),
        ('black', 'Black'),
        ('islander', 'Native Hawaiian or Other Pacific Islander'),
        ('indian', 'Indian'),
        ('asian', 'Asian'),
        ('native', 'Native American or Alaska Native'),
        ('mixed', 'Mixed Race'),
        ('other', 'Other')
    )

    INCOME = (
        ('less_1k', 'Less than $1,000'),
        ('1k', '$1,000 - $1,999'),
        ('2.5k', '$2,500 - $4,999'),
        ('5k', '$5,000 - $7,499'),
        ('7.5k', '$7,500 - $9,999'),
        ('10k', '$10,000 - $14,999'),
        ('15k', '$15,000 - $24,999'),
        ('25k', '$25,000 - $39,999'),
        ('40k', '$40,000 - $59,999'),
        ('60k', '$60,000 - $74,999'),
        ('75k', '$75,000 - $99,999'),
        ('100k', '$100,000 - $149,999'),
        ('150k', '$150,000 - $199,999'),
        ('200k', '$200,000 - $299,999'),
        ('300k_more', '$300,000 or more')
    )

    EDUCATION = (
        ('some_high', 'Some High School, No Degree'),
        ('high', 'High School Degree or Equivalent'),
        ('some_college', 'Some College, No Degree'),
        ('associates', 'Associates Degree'),
        ('bachelors', 'Bachelors Degree'),
        ('masters', 'Graduate Degree, Masters'),
        ('doctorate', 'Graduate Degree, Doctorate')
    )

    user = models.OneToOneField(User, related_name='profile')
    gender = models.CharField(max_length=1, choices=GENDER, blank=True, null=True)
    purpose_of_use = models.CharField(max_length=64, choices=PURPOSE_OF_USE, blank=True, null=True)
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
    income = models.CharField(max_length=9, choices=INCOME, blank=True, null=True)
    education = models.CharField(max_length=12, choices=EDUCATION, blank=True, null=True)
    unspecified_responses = JSONField(null=True)
    handle = models.CharField(max_length=32, db_index=True, blank=False, unique=True)


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
    user = models.OneToOneField(User, related_name='preferences')
    language = models.ForeignKey(Language, null=True, blank=True)
    currency = models.ForeignKey(Currency, null=True, blank=True)
    login_alerts = models.SmallIntegerField(default=0)
    auto_accept = models.BooleanField(default=False)
    new_tasks_notifications = models.BooleanField(default=True)
    aux_attributes = JSONField(default={})


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
        df = pd.DataFrame(pd.read_csv(self.file, sep=delimiter, encoding='utf-8'))
        df = df.where((pd.notnull(df)), None)
        return df.to_dict(orient='records')

    def delete(self, *args, **kwargs):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, self.file.url[1:])
        os.remove(path)
        super(BatchFile, self).delete(*args, **kwargs)


class ProjectQueryset(models.query.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)

    def inactive(self):
        return self.filter(deleted_at__isnull=False)

    def filter_by_boomerang(self, worker, sort_by='-boomerang'):
        worker_cache = get_worker_cache(worker.id)
        worker_data = json.dumps(worker_cache)

        # noinspection SqlResolve
        query = '''
            WITH projects AS (
                SELECT
                    ratings.project_id,
                    ratings.min_rating new_min_rating,
                    requester_ratings.requester_rating,
                    requester_ratings.raw_rating,
                    p_available.remaining available_tasks
                FROM crowdsourcing_project p
                INNER JOIN (SELECT
                      p.id,
                      count(t.id) remaining

                    FROM crowdsourcing_task t INNER JOIN (SELECT
                                                            group_id,
                                                            max(id) id
                                                          FROM crowdsourcing_task
                                                          WHERE deleted_at IS NULL
                                                          GROUP BY group_id) t_max ON t_max.id = t.id
                      INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                      INNER JOIN (
                                   SELECT
                                     t.group_id,
                                     sum(t.own)    own,
                                     sum(t.others) others
                                   FROM (
                                          SELECT
                                            t.group_id,
                                            CASE WHEN (tw.worker_id = (%(worker_id)s) AND tw.status <> 6)
                                                    or tw.is_qualified is FALSE
                                              THEN 1
                                            ELSE 0 END own,
                                            CASE WHEN (tw.worker_id IS NOT NULL AND tw.worker_id <> (%(worker_id)s))
                                                AND tw.status NOT IN (4, 6, 7)
                                              THEN 1
                                            ELSE 0 END others
                                          FROM crowdsourcing_task t
                                            LEFT OUTER JOIN crowdsourcing_taskworker tw ON (t.id =
                                                                                            tw.task_id)
                                          WHERE t.exclude_at IS NULL AND t.deleted_at IS NULL) t
                                   GROUP BY t.group_id) t_count ON t_count.group_id = t.group_id
                    WHERE t_count.own = 0 AND t_count.others < p.repetition
                    GROUP BY p.id) p_available ON p_available.id = p.id

                INNER JOIN (
                    SELECT
                        u.id,
                        u.username,
                        CASE WHEN e.id IS NOT NULL
                          THEN TRUE
                        ELSE FALSE END is_denied
                    FROM auth_user u
                        LEFT OUTER JOIN crowdsourcing_requesteraccesscontrolgroup g
                          ON g.requester_id = u.id AND g.type = 2 AND g.is_global = TRUE
                        LEFT OUTER JOIN crowdsourcing_workeraccesscontrolentry e
                          ON e.group_id = g.id AND e.worker_id = (%(worker_id)s)) requester
                          ON requester.id=p.owner_id
                        LEFT OUTER JOIN (
                            SELECT
                                qualification_id,
                                json_agg(i.expression::JSON) expressions
                            FROM crowdsourcing_qualificationitem i
                                where i.scope = 'project'
                            GROUP BY i.qualification_id
                        ) quals
                    ON quals.qualification_id = p.qualification_id
                INNER JOIN get_min_project_ratings() ratings
                    ON p.id = ratings.project_id
                LEFT OUTER JOIN (
                    SELECT
                        requester_id,
                        requester_rating AS raw_rating,
                        CASE WHEN requester_rating IS NULL AND requester_avg_rating
                                                            IS NOT NULL
                        THEN requester_avg_rating
                        WHEN requester_rating IS NULL AND requester_avg_rating IS NULL
                        THEN 1.99
                        WHEN requester_rating IS NOT NULL AND requester_avg_rating IS NULL
                        THEN requester_rating
                        ELSE requester_rating + 0.1 * requester_avg_rating END requester_rating
                   FROM get_requester_ratings(%(worker_id)s)) requester_ratings
                    ON requester_ratings.requester_id = ratings.owner_id
                  INNER JOIN (SELECT
                                     requester_id,
                                     CASE WHEN worker_rating IS NULL AND worker_avg_rating
                                                                         IS NOT NULL
                                       THEN worker_avg_rating
                                     WHEN worker_rating IS NULL AND worker_avg_rating IS NULL
                                       THEN 1.99
                                     WHEN worker_rating IS NOT NULL AND worker_avg_rating IS NULL
                                       THEN worker_rating
                                     ELSE worker_rating + 0.1 * worker_avg_rating END worker_rating
                                   FROM get_worker_ratings(%(worker_id)s)) worker_ratings
                    ON worker_ratings.requester_id = ratings.owner_id
                       AND (worker_ratings.worker_rating >= ratings.min_rating or p.enable_boomerang is FALSE 
                       or p.owner_id = %(worker_id)s)
                WHERE coalesce(p.deadline, NOW() + INTERVAL '1 minute') > NOW() AND p.status = 3 AND deleted_at IS NULL
                  AND (requester.is_denied = FALSE OR p.enable_blacklist = FALSE)
                  AND is_worker_qualified(quals.expressions, (%(worker_data)s)::JSON)
                ORDER BY requester_rating DESC, ratings.project_id desc
                    )
            select p.id, p.name, p.price, p.owner_id, p.created_at, p.allow_feedback,
            p.is_prototype, projects.requester_rating, projects.raw_rating, projects.available_tasks,
            up.handle requester_handle, p.published_at
            FROM crowdsourcing_project p
            INNER JOIN crowdsourcing_userprofile up on up.user_id = p.owner_id
            INNER JOIN projects ON projects.project_id = p.id ORDER BY case when %(sort_by)s='-boomerang'
            then requester_rating when %(sort_by)s='-available_tasks' then available_tasks
              when %(sort_by)s='-published_at' then 12 when %(sort_by)s='-price' then p.price
                end desc nulls last, p.id desc;
            '''
        return self.raw(query, params={
            'worker_id': worker.id,
            'st_in_progress': Project.STATUS_IN_PROGRESS,
            'worker_data': worker_data,
            'sort_by': sort_by
        })


class Project(TimeStampable, Archivable, Revisable):
    STATUS_DRAFT = 1
    STATUS_PUBLISHED = 2
    STATUS_IN_PROGRESS = 3
    STATUS_COMPLETED = 4
    STATUS_PAUSED = 5
    STATUS_CROWD_REJECTED = 6
    STATUS_ARCHIVED = 7

    STATUS = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_PAUSED, 'Paused'),
        (STATUS_CROWD_REJECTED, 'Rejected'),
        (STATUS_ARCHIVED, 'Archived'),
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

    name = models.CharField(max_length=256, default="Untitled Project",
                            error_messages={'required': "Please enter the project name!"})
    description = models.TextField(null=True, max_length=2048, blank=True)
    owner = models.ForeignKey(User, related_name='projects')
    parent = models.ForeignKey('self', related_name='projects', null=True, on_delete=models.SET_NULL)
    template = models.ForeignKey(Template, null=True)
    categories = models.ManyToManyField(Category, through='ProjectCategory')
    keywords = models.TextField(null=True, blank=True)

    status = models.IntegerField(choices=STATUS, default=STATUS_DRAFT)
    qualification = models.ForeignKey('Qualification', null=True)

    price = models.DecimalField(decimal_places=2, max_digits=19, null=True)
    aux_attributes = JSONField(null=True, default={'sort_results_by': 'worker_id'})
    repetition = models.IntegerField(default=1)
    max_tasks = models.PositiveIntegerField(null=True, default=None)

    is_micro = models.BooleanField(default=True)
    is_prototype = models.BooleanField(default=True)
    is_api_only = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)
    is_review = models.BooleanField(default=False)
    # has_review = models.BooleanField(default=False)

    timeout = models.DurationField(null=True, default=settings.DEFAULT_TASK_TIMEOUT)
    deadline = models.DateTimeField(null=True)
    task_time = models.DurationField(null=True)

    has_data_set = models.BooleanField(default=False)
    data_set_location = models.CharField(max_length=256, null=True, blank=True)
    batch_files = models.ManyToManyField(BatchFile, through='ProjectBatchFile')

    min_rating = models.FloatField(default=3.0)
    previous_min_rating = models.FloatField(default=3.0)
    tasks_in_progress = models.IntegerField(default=0)
    rating_updated_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    allow_feedback = models.BooleanField(default=True)
    feedback_permissions = models.IntegerField(choices=PERMISSION, default=PERMISSION_ORW_WRW)
    enable_blacklist = models.BooleanField(default=True)
    enable_whitelist = models.BooleanField(default=True)

    post_mturk = models.BooleanField(default=False)
    publish_at = models.DateTimeField(null=True)
    published_at = models.DateTimeField(null=True)
    last_opened_at = models.DateTimeField(null=True)
    allow_price_per_task = models.BooleanField(default=False)
    task_price_field = models.CharField(max_length=32, null=True)

    amount_due = models.DecimalField(decimal_places=2, max_digits=8, default=0)

    discussion_link = models.TextField(null=True, blank=True)
    topic_id = models.IntegerField(null=True, default=-1)
    post_id = models.IntegerField(null=True, default=-1)
    enable_boomerang = models.BooleanField(default=True)

    objects = ProjectQueryset.as_manager()

    class Meta:
        index_together = [['deadline', 'status', 'min_rating', 'deleted_at'], ['owner', 'deleted_at', 'created_at']]


class ProjectWorkerToRate(TimeStampable):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    batch = models.ForeignKey('Batch', on_delete=models.SET_NULL, null=True)
    worker = models.ForeignKey(User)


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


class TemplateItem(TimeStampable, Revisable):
    ROLE_DISPLAY = 'display'
    ROLE_INPUT = 'input'

    ROLE = (
        (ROLE_DISPLAY, 'Display'),
        (ROLE_INPUT, 'Input'),
    )
    name = models.CharField(max_length=128, default='')
    template = models.ForeignKey(Template, related_name='items', on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE, default=ROLE_DISPLAY)
    type = models.CharField(max_length=16, db_index=True)
    sub_type = models.CharField(max_length=16, null=True)
    position = models.IntegerField(null=True)
    required = models.BooleanField(default=True)
    predecessor = models.ForeignKey('self', null=True, related_name='successors', on_delete=models.SET_NULL,
                                    db_index=True)
    aux_attributes = JSONField()

    class Meta:
        ordering = ['position']


class TemplateItemProperties(TimeStampable):
    template_item = models.ForeignKey(TemplateItem, related_name='properties')
    attribute = models.CharField(max_length=128)
    operator = models.CharField(max_length=128)
    value1 = models.CharField(max_length=128)
    value2 = models.CharField(max_length=128)


class CollectiveRejection(TimeStampable, Archivable):
    REASON_LOW_PAY = 1
    REASON_INAPPROPRIATE = 2
    REASON_OTHER = 3

    REASON = (
        (REASON_LOW_PAY, 'The pay is too low for the amount of work'),
        (REASON_INAPPROPRIATE, 'The content is offensive or inappropriate'),
        (REASON_OTHER, 'Other')
    )
    reason = models.IntegerField(choices=REASON)
    detail = models.CharField(max_length=1024, null=True, blank=True)


class Batch(TimeStampable):
    parent = models.ForeignKey('Batch', null=True)


class Task(TimeStampable, Archivable, Revisable):
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    data = JSONField(null=True)
    exclude_at = models.ForeignKey(Project, related_name='excluded_tasks', db_column='exclude_at',
                                   null=True, on_delete=models.SET_NULL)
    row_number = models.IntegerField(null=True, db_index=True)
    rerun_key = models.CharField(max_length=64, db_index=True, null=True)
    batch = models.ForeignKey('Batch', related_name='tasks', null=True, on_delete=models.CASCADE)
    hash = models.CharField(max_length=64, db_index=True)

    min_rating = models.FloatField(default=3.0)
    rating_updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=19, null=True)

    class Meta:
        index_together = (('rerun_key', 'hash',),)


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
    status = models.IntegerField(choices=STATUS, default=STATUS_IN_PROGRESS, db_index=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    collective_rejection = models.OneToOneField(CollectiveRejection, null=True)
    charge = models.ForeignKey('StripeCharge', null=True)
    submitted_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, db_index=True)
    started_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    approved_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    returned_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    is_qualified = models.BooleanField(default=True, db_index=True)
    attempt = models.SmallIntegerField(default=0)
    auto_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'worker')


class TaskWorkerSession(TimeStampable):
    started_at = models.DateTimeField(auto_now_add=False, auto_now=False, db_index=True)
    ended_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, db_index=True)
    task_worker = models.ForeignKey('TaskWorker', related_name='sessions')


class TaskWorkerResult(TimeStampable, Archivable):
    task_worker = models.ForeignKey(TaskWorker, related_name='results', on_delete=models.CASCADE)
    result = JSONField(null=True)
    attachment = models.ForeignKey('FileResponse', null=True)
    template_item = models.ForeignKey(TemplateItem, related_name='+')


class FileResponse(TimeStampable):
    file = models.FileField(upload_to='responses/%Y/%m/%d/')
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User)
    hash_sha512 = models.CharField(max_length=128, null=True, blank=True)


class WorkerProjectScore(TimeStampable):
    project_group_id = models.IntegerField()
    worker = models.ForeignKey(User, related_name='project_scores')
    mu = models.FloatField(default=25.000)
    sigma = models.FloatField(default=8.333)


class WorkerMatchScore(TimeStampable):
    worker = models.ForeignKey(TaskWorker, related_name='match_scores')
    project_score = models.ForeignKey(WorkerProjectScore, related_name='match_scores')
    mu = models.FloatField()
    sigma = models.FloatField()


class MatchGroup(TimeStampable):
    batch = models.ForeignKey(Batch, related_name='match_group')
    rerun_key = models.CharField(max_length=64, null=True, db_index=True)
    hash = models.CharField(max_length=64, db_index=True)
    parent = models.ForeignKey('self', related_name='children_groups', null=True)

    class Meta:
        index_together = (('rerun_key', 'hash',),)


class Match(TimeStampable):
    STATUS_CREATED = 1
    STATUS_COMPLETED = 2
    STATUS = (
        (STATUS_CREATED, 'Created'),
        (STATUS_COMPLETED, 'Completed'),
    )
    status = models.IntegerField(choices=STATUS, default=STATUS_CREATED)
    submitted_at = models.DateTimeField(null=True)
    group = models.ForeignKey(MatchGroup, related_name='matches')
    task = models.ForeignKey(Task, related_name='matches', null=True)


class MatchWorker(TimeStampable):
    match = models.ForeignKey(Match, related_name='workers')
    task_worker = models.ForeignKey(TaskWorker, related_name='matches')
    mu = models.FloatField(null=True)
    sigma = models.FloatField(null=True)
    old_mu = models.FloatField(default=25.0, null=True)
    old_sigma = models.FloatField(default=8.333, null=True)


class ActivityLog(TimeStampable):
    """
        Track all user's activities: Create, Update and Delete
    """
    activity = models.CharField(max_length=512)
    author = models.ForeignKey(User, related_name='activities')


class Qualification(TimeStampable):
    TYPE_STRICT = 1
    TYPE_FLEXIBLE = 2
    name = models.CharField(max_length=64, null=True)
    description = models.CharField(max_length=512, null=True)
    owner = models.ForeignKey(User, related_name='qualifications')
    TYPE = (
        (TYPE_STRICT, "Strict"),
        (TYPE_FLEXIBLE, 'Flexible')
    )
    type = models.IntegerField(choices=TYPE, default=TYPE_STRICT)


class QualificationItem(TimeStampable):
    qualification = models.ForeignKey(Qualification, related_name='items', on_delete=models.CASCADE)
    expression = JSONField()
    position = models.SmallIntegerField(null=True)
    group = models.SmallIntegerField(default=1)
    scope = models.CharField(max_length=32, default='project', db_index=True)


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
    task = models.ForeignKey(Task, null=True)

    class Meta:
        index_together = [
            ['origin', 'target'],
            ['origin', 'target', 'updated_at', 'origin_type']
        ]


class RawRatingFeedback(TimeStampable):
    requester = models.ForeignKey(User, related_name='raw_feedback')
    worker = models.ForeignKey(User, related_name='+')
    weight = models.FloatField(default=0)
    task = models.ForeignKey(Task, null=True)
    is_excluded = models.BooleanField(default=False)

    class Meta:
        unique_together = ('requester', 'worker', 'task')
        index_together = ('requester', 'worker', 'task', 'is_excluded')


class BoomerangLog(TimeStampable):
    object_id = models.PositiveIntegerField()
    object_type = models.CharField(max_length=8, default='project')
    min_rating = models.FloatField(default=3.0)
    rating_updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    reason = models.CharField(max_length=64, null=True)


class Conversation(TimeStampable, Archivable):
    subject = models.CharField(max_length=64)
    sender = models.ForeignKey(User, related_name='conversations')
    recipients = models.ManyToManyField(User, through='ConversationRecipient')


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


class Message(TimeStampable, Archivable):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages')
    body = models.TextField(max_length=8192)
    recipients = models.ManyToManyField(User, through='MessageRecipient')


class MessageRecipient(TimeStampable, Archivable):
    STATUS_SENT = 1
    STATUS_DELIVERED = 2
    STATUS_READ = 3

    STATUS = (
        (STATUS_SENT, 'Sent'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_READ, 'Read')
    )

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS, default=STATUS_SENT)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)


class EmailNotification(TimeStampable):
    # use updated_at to check last notification sent
    recipient = models.OneToOneField(User)


class Comment(TimeStampable, Archivable):
    sender = models.ForeignKey(User, related_name='comments')
    body = models.TextField(max_length=8192)
    parent = models.ForeignKey('self', related_name='comments', null=True)

    class Meta:
        ordering = ['created_at']


class ProjectComment(TimeStampable, Archivable):
    project = models.ForeignKey(Project, related_name='comments')
    comment = models.ForeignKey(Comment)
    ready_for_launch = models.NullBooleanField()
    aux_attributes = JSONField(default={}, null=True)


class TaskComment(TimeStampable, Archivable):
    task = models.ForeignKey(Task, related_name='comments')
    comment = models.ForeignKey(Comment)


class FinancialAccount(TimeStampable, Activable):
    TYPE_WORKER = 1
    TYPE_REQUESTER = 2
    TYPE_ESCROW = 3

    TYPE = (
        (TYPE_WORKER, 'Earnings'),
        (TYPE_REQUESTER, 'Deposits'),
        (TYPE_ESCROW, 'Escrow')
    )
    owner = models.ForeignKey(User, related_name='financial_accounts', null=True)
    type = models.IntegerField(choices=TYPE)
    balance = models.DecimalField(default=0, decimal_places=4, max_digits=19)
    is_system = models.BooleanField(default=False)


class RequesterAccessControlGroup(TimeStampable):
    TYPE_ALLOW = 1
    TYPE_DENY = 2
    TYPE = (
        (TYPE_ALLOW, "allow"),
        (TYPE_DENY, "deny")
    )
    requester = models.ForeignKey(User, related_name="access_groups")

    type = models.SmallIntegerField(choices=TYPE, default=TYPE_ALLOW)
    name = models.CharField(max_length=256, null=True)
    is_global = models.BooleanField(default=False)

    class Meta:
        index_together = [['requester', 'type', 'is_global']]


class WorkerAccessControlEntry(TimeStampable):
    worker = models.ForeignKey(User)
    group = models.ForeignKey(RequesterAccessControlGroup, related_name='entries')

    class Meta:
        unique_together = ('group', 'worker')
        index_together = [['group', 'worker']]


class ReturnFeedback(TimeStampable, Archivable):
    body = models.TextField(max_length=8192)
    task_worker = models.ForeignKey(TaskWorker, related_name='return_feedback', on_delete=models.CASCADE)
    notification_sent = models.BooleanField(default=False, db_index=True)
    notification_sent_at = models.DateTimeField(null=True, auto_now_add=False, auto_now=False)

    class Meta:
        ordering = ['-created_at']


class Error(TimeStampable, Archivable):
    code = models.CharField(max_length=16)
    message = models.CharField(max_length=256)
    trace = models.CharField(max_length=4096, null=True)
    owner = models.ForeignKey(User, null=True, related_name='errors')


class StripeAccount(TimeStampable, Verifiable, StripeObject):
    owner = models.OneToOneField(User, related_name='stripe_account')


class StripeCustomer(TimeStampable, StripeObject):
    owner = models.OneToOneField(User, related_name='stripe_customer')
    account_balance = models.IntegerField(default=0)


class StripeCharge(TimeStampable, StripeObject):
    customer = models.ForeignKey(StripeCustomer, related_name='charges')
    expired = models.BooleanField(default=False)
    expired_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    balance = models.IntegerField()
    discount_applied = models.BooleanField(default=False)
    raw_amount = models.IntegerField()
    discount = models.FloatField(default=1.0)

    class Meta:
        index_together = (('created_at',), ('created_at', 'customer'))


class StripeRefund(TimeStampable, StripeObject):
    charge = models.ForeignKey(StripeCharge, related_name='refunds')


class StripeTransfer(TimeStampable, StripeObject):
    destination = models.ForeignKey(User, related_name='received_transfers')


class StripeTransferReversal(TimeStampable, StripeObject):
    transfer = models.ForeignKey(StripeTransfer, related_name='reversals')


class ProjectNotificationPreference(TimeStampable):
    project_group_id = models.IntegerField()
    worker = models.ForeignKey(User, related_name='notification_preferences')
    notify = models.BooleanField(default=True)

    class Meta:
        unique_together = ('project_group_id', 'worker')


class WorkerProjectNotification(TimeStampable):
    project = models.ForeignKey('Project')
    worker = models.ForeignKey(User, related_name='project_notifications')


class WorkerBonus(TimeStampable):
    worker = models.ForeignKey(User, related_name='bonuses_received')
    requester = models.ForeignKey(User, related_name='bonuses_given')
    reason = models.CharField(max_length=256, null=True, blank=True)
    models.ForeignKey(Project, related_name='worker_bonuses', null=True)
    charge = models.ForeignKey('StripeCharge', null=True)
    amount = models.IntegerField()


class ProjectPreview(TimeStampable):
    project = models.ForeignKey('Project')
    user = models.ForeignKey(User)
