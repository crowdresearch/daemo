# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import oauth2client.django_orm
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [(b'crowdsourcing', '0001_initial'), (b'crowdsourcing', '0002_auto_20150707_0935'), (b'crowdsourcing', '0003_project_hasmultipletasks'), (b'crowdsourcing', '0004_auto_20150707_1227'), (b'crowdsourcing', '0005_auto_20150707_1244'), (b'crowdsourcing', '0006_auto_20150707_1259'), (b'crowdsourcing', '0007_auto_20150707_1310'), (b'crowdsourcing', '0008_auto_20150707_1355'), (b'crowdsourcing', '0009_auto_20150707_1459'), (b'crowdsourcing', '0010_auto_20150707_2247'), (b'crowdsourcing', '0011_auto_20150708_1151'), (b'crowdsourcing', '0012_auto_20150708_2216'), (b'crowdsourcing', '0013_auto_20150708_2359'), (b'crowdsourcing', '0014_auto_20150709_0139'), (b'crowdsourcing', '0015_auto_20150709_0149'), (b'crowdsourcing', '0016_auto_20150709_0201'), (b'crowdsourcing', '0017_auto_20150709_0204'), (b'crowdsourcing', '0018_auto_20150709_0208'), (b'crowdsourcing', '0019_conversationrecipient_date_added'), (b'crowdsourcing', '0020_auto_20150709_0229'), (b'crowdsourcing', '0021_auto_20150728_2148'), (b'crowdsourcing', '0022_auto_20150728_2153'), (b'crowdsourcing', '0021_auto_20150722_2229'), (b'crowdsourcing', '0023_merge'), (b'crowdsourcing', '0024_file'), (b'crowdsourcing', '0025_auto_20150805_1718'), (b'crowdsourcing', '0026_workerrequesterrating'), (b'crowdsourcing', '0027_auto_20150808_1301'), (b'crowdsourcing', '0028_module_is_micro'), (b'crowdsourcing', '0029_taskworker_task_status'), (b'crowdsourcing', '0030_module_is_prototype'), (b'crowdsourcing', '0031_auto_20150814_1743'), (b'crowdsourcing', '0032_auto_20150814_2009'), (b'crowdsourcing', '0033_templateitem_position'), (b'crowdsourcing', '0034_auto_20150817_2049'), (b'crowdsourcing', '0033_auto_20150817_2056'), (b'crowdsourcing', '0035_merge'), (b'crowdsourcing', '0036_auto_20150817_2226'), (b'crowdsourcing', '0037_auto_20150818_1811'), (b'crowdsourcing', '0038_module_min_rating'), (b'crowdsourcing', '0039_auto_20150824_2009'), (b'crowdsourcing', '0040_auto_20150824_2013'), (b'crowdsourcing', '0041_auto_20150825_0240'), (b'crowdsourcing', '0042_auto_20150825_1745'), (b'crowdsourcing', '0042_auto_20150825_1715'), (b'crowdsourcing', '0043_merge'), (b'crowdsourcing', '0044_auto_20150828_1857'), (b'crowdsourcing', '0045_auto_20150901_0120'), (b'crowdsourcing', '0046_requesterexperiment_taskranking_workerexperiment'), (b'crowdsourcing', '0047_auto_20150913_1148'), (b'crowdsourcing', '0048_auto_20150913_2209'), (b'crowdsourcing', '0049_auto_20150914_0436'), (b'crowdsourcing', '0050_submodule'), (b'crowdsourcing', '0051_auto_20150914_0948'), (b'crowdsourcing', '0052_submodule_result_per_round'), (b'crowdsourcing', '0053_auto_20150914_1540'), (b'crowdsourcing', '0054_submodule_hours_before_results'), (b'crowdsourcing', '0055_auto_20150914_1647'), (b'crowdsourcing', '0056_submodule_taskworkers'), (b'crowdsourcing', '0057_auto_20150914_1810'), (b'crowdsourcing', '0058_workerexperiment_feedback_required'), (b'crowdsourcing', '0059_auto_20150918_1655'), (b'crowdsourcing', '0060_auto_20151019_2116'), (b'crowdsourcing', '0061_auto_20151019_2152'), (b'crowdsourcing', '0062_userprofile_last_active'), (b'crowdsourcing', '0063_auto_20151119_2242')]

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('type', models.CharField(max_length=16)),
                ('email', models.EmailField(max_length=254)),
                ('access_token', models.TextField(max_length=2048)),
                ('root', models.CharField(max_length=256)),
                ('is_active', models.IntegerField()),
                ('quota', models.BigIntegerField()),
                ('used_space', models.BigIntegerField()),
                ('assigned_space', models.BigIntegerField()),
                ('status', models.IntegerField(default=models.BigIntegerField())),
            ],
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity', models.CharField(max_length=512)),
                ('created_timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street', models.CharField(max_length=128, error_messages={b'required': b'Please specify the street name!'})),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, error_messages={b'required': b'Please enter the category name!'})),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(to='crowdsourcing.Category', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, error_messages={b'required': b'Please specify the city!'})),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, error_messages={b'required': b'Please specify the country!'})),
                ('code', models.CharField(max_length=8, error_messages={b'required': b'Please specify the country code!'})),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CredentialsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credential', oauth2client.django_orm.CredentialsField(null=True)),
                ('account', models.ForeignKey(to='crowdsourcing.AccountModel')),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('iso_code', models.CharField(max_length=8)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='FlowModel',
            fields=[
                ('id', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('flow', oauth2client.django_orm.FlowField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, error_messages={b'required': b'Please specify the language!'})),
                ('iso_code', models.CharField(max_length=8)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, error_messages={b'required': b'Please enter the module name!'})),
                ('description', models.TextField(error_messages={b'required': b'Please enter the module description!'})),
                ('keywords', models.TextField()),
                ('status', models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'In Review'), (3, b'In Progress'), (4, b'Finished')])),
                ('repetition', models.IntegerField()),
                ('module_timeout', models.IntegerField()),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ModuleCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(to='crowdsourcing.Category')),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
            ],
        ),
        migrations.CreateModel(
            name='ModuleRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
            ],
        ),
        migrations.CreateModel(
            name='ModuleReview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('annonymous', models.BooleanField(default=False)),
                ('comments', models.TextField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
            ],
        ),
        migrations.CreateModel(
            name='PasswordResetModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reset_key', models.CharField(max_length=40)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, error_messages={b'required': b'Please enter the project name!'})),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(default=b'', max_length=1024)),
                ('keywords', models.TextField()),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(to='crowdsourcing.Category')),
                ('project', models.ForeignKey(to='crowdsourcing.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectRequester',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(to='crowdsourcing.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Qualification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(default=1, choices=[(1, b'Strict'), (2, b'Flexible')])),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
            ],
        ),
        migrations.CreateModel(
            name='QualificationItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attribute', models.CharField(max_length=128)),
                ('operator', models.CharField(max_length=128)),
                ('value1', models.CharField(max_length=128)),
                ('value2', models.CharField(max_length=128)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('qualification', models.ForeignKey(to='crowdsourcing.Qualification')),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, error_messages={'required': 'Please specify the region!'})),
                ('code', models.CharField(max_length=16, error_messages={'required': 'Please specify the region code!'})),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activation_key', models.CharField(max_length=40)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Requester',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='RequesterRanking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('requester_name', models.CharField(max_length=128)),
                ('requester_payRank', models.FloatField()),
                ('requester_fairRank', models.FloatField()),
                ('requester_speedRank', models.FloatField()),
                ('requester_communicationRank', models.FloatField()),
                ('requester_numberofReviews', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=32, error_messages={b'unique': b'The role %(value)r already exists. Please provide another name!', b'required': b'Please specify the role name!'})),
                ('is_active', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, error_messages={b'required': b'Please enter the skill name!'})),
                ('description', models.CharField(max_length=512, error_messages={b'required': b'Please enter the skill description!'})),
                ('verified', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(to='crowdsourcing.Skill', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'Accepted'), (3, b'Assigned'), (4, b'Finished')])),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('price', models.FloatField(default=0)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
            ],
        ),
        migrations.CreateModel(
            name='TaskWorker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('task', models.ForeignKey(to='crowdsourcing.Task')),
            ],
        ),
        migrations.CreateModel(
            name='TaskWorkerResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.TextField()),
                ('status', models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'Accepted'), (3, b'Rejected')])),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('task_worker', models.ForeignKey(to='crowdsourcing.TaskWorker')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, error_messages={b'required': b'Please enter the template name!'})),
                ('source_html', models.TextField()),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(to='crowdsourcing.Requester')),
            ],
        ),
        migrations.CreateModel(
            name='TemplateItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, error_messages={b'required': b'Please enter the name of the template item!'})),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('template', models.ForeignKey(to='crowdsourcing.Template')),
            ],
        ),
        migrations.CreateModel(
            name='TemplateItemProperties',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attribute', models.CharField(max_length=128)),
                ('operator', models.CharField(max_length=128)),
                ('value1', models.CharField(max_length=128)),
                ('value2', models.CharField(max_length=128)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('template_item', models.ForeignKey(to='crowdsourcing.TemplateItem')),
            ],
        ),
        migrations.CreateModel(
            name='TemporaryFlowModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=16)),
                ('email', models.EmailField(max_length=254)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(to='crowdsourcing.Country')),
            ],
        ),
        migrations.CreateModel(
            name='UserLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('language', models.ForeignKey(to='crowdsourcing.Language')),
            ],
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('login_alerts', models.SmallIntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('currency', models.ForeignKey(to='crowdsourcing.Currency')),
                ('language', models.ForeignKey(to='crowdsourcing.Language')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('birthday', models.DateField(null=True, error_messages={b'invalid': b'Please enter a correct date format'})),
                ('verified', models.BooleanField(default=False)),
                ('picture', models.BinaryField(null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('worker_alias', models.CharField(max_length=32, error_messages={b'required': b'Please enter an alias!'})),
                ('requester_alias', models.CharField(max_length=32, error_messages={b'required': b'Please enter an alias!'})),
                ('address', models.ForeignKey(to='crowdsourcing.Address', null=True)),
                ('friends', models.ManyToManyField(to=b'crowdsourcing.UserProfile', through='crowdsourcing.Friendship')),
                ('languages', models.ManyToManyField(to=b'crowdsourcing.Language', through='crowdsourcing.UserLanguage')),
                ('nationality', models.ManyToManyField(to=b'crowdsourcing.Country', through='crowdsourcing.UserCountry')),
            ],
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('role', models.ForeignKey(to='crowdsourcing.Role')),
                ('user_profile', models.ForeignKey(to='crowdsourcing.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('profile', models.OneToOneField(to='crowdsourcing.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='WorkerModuleApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Created'), (2, 'Accepted'), (3, 'Rejected')])),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
                ('worker', models.ForeignKey(to='crowdsourcing.Worker')),
            ],
        ),
        migrations.CreateModel(
            name='WorkerSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.IntegerField(null=True)),
                ('verified', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('skill', models.ForeignKey(to='crowdsourcing.Skill')),
                ('worker', models.ForeignKey(to='crowdsourcing.Worker')),
            ],
        ),
        migrations.AddField(
            model_name='worker',
            name='skills',
            field=models.ManyToManyField(to=b'crowdsourcing.Skill', through='crowdsourcing.WorkerSkill'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='roles',
            field=models.ManyToManyField(to=b'crowdsourcing.Role', through='crowdsourcing.UserRole'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userlanguage',
            name='user',
            field=models.ForeignKey(to='crowdsourcing.UserProfile'),
        ),
        migrations.AddField(
            model_name='usercountry',
            name='user',
            field=models.ForeignKey(to='crowdsourcing.UserProfile'),
        ),
        migrations.AddField(
            model_name='taskworkerresult',
            name='template_item',
            field=models.ForeignKey(to='crowdsourcing.TemplateItem'),
        ),
        migrations.AddField(
            model_name='taskworker',
            name='worker',
            field=models.ForeignKey(to='crowdsourcing.Worker'),
        ),
        migrations.AddField(
            model_name='requester',
            name='profile',
            field=models.OneToOneField(to='crowdsourcing.UserProfile'),
        ),
        migrations.AddField(
            model_name='projectrequester',
            name='requester',
            field=models.ForeignKey(to='crowdsourcing.Requester'),
        ),
        migrations.AddField(
            model_name='project',
            name='categories',
            field=models.ManyToManyField(to=b'crowdsourcing.Category', through='crowdsourcing.ProjectCategory'),
        ),
        migrations.AddField(
            model_name='project',
            name='collaborators',
            field=models.ManyToManyField(to=b'crowdsourcing.Requester', through='crowdsourcing.ProjectRequester'),
        ),
        migrations.AddField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(related_name='project_owner', to='crowdsourcing.Requester'),
        ),
        migrations.AddField(
            model_name='modulereview',
            name='worker',
            field=models.ForeignKey(to='crowdsourcing.Worker'),
        ),
        migrations.AddField(
            model_name='modulerating',
            name='worker',
            field=models.ForeignKey(to='crowdsourcing.Worker'),
        ),
        migrations.AddField(
            model_name='module',
            name='categories',
            field=models.ManyToManyField(to=b'crowdsourcing.Category', through='crowdsourcing.ModuleCategory'),
        ),
        migrations.AddField(
            model_name='module',
            name='owner',
            field=models.ForeignKey(to='crowdsourcing.Requester'),
        ),
        migrations.AddField(
            model_name='module',
            name='project',
            field=models.ForeignKey(to='crowdsourcing.Project'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='user_source',
            field=models.ForeignKey(related_name='user_source', to='crowdsourcing.UserProfile'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='user_target',
            field=models.ForeignKey(related_name='user_target', to='crowdsourcing.UserProfile'),
        ),
        migrations.AddField(
            model_name='country',
            name='region',
            field=models.ForeignKey(to='crowdsourcing.Region'),
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(to='crowdsourcing.Country'),
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.ForeignKey(to='crowdsourcing.City'),
        ),
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.ForeignKey(to='crowdsourcing.Country'),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accountmodel',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='projectcategory',
            unique_together=set([('project', 'category')]),
        ),
        migrations.AlterUniqueTogether(
            name='modulereview',
            unique_together=set([('worker', 'module')]),
        ),
        migrations.AlterUniqueTogether(
            name='modulerating',
            unique_together=set([('worker', 'module')]),
        ),
        migrations.AlterUniqueTogether(
            name='modulecategory',
            unique_together=set([('category', 'module')]),
        ),
        migrations.AddField(
            model_name='module',
            name='price',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='module',
            name='module_timeout',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='module',
            name='repetition',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'In Review'), (3, b'In Progress'), (4, b'Completed')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='keywords',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='save_to_drive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='module',
            name='data_set_location',
            field=models.CharField(default=b'No data set', max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='module',
            name='has_data_set',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='module',
            name='task_time',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='template',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='template',
            name='share_with_others',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='templateitem',
            name='data_source',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='templateitem',
            name='icon',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='templateitem',
            name='id_string',
            field=models.CharField(default='Label1', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='layout',
            field=models.CharField(default='column', max_length=16),
        ),
        migrations.AddField(
            model_name='templateitem',
            name='role',
            field=models.CharField(default='display', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='sub_type',
            field=models.CharField(default='h4', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='type',
            field=models.CharField(default='label', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='values',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='keywords',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='template',
            name='source_html',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='template',
            name='owner',
            field=models.ForeignKey(to='crowdsourcing.UserProfile'),
        ),
        migrations.CreateModel(
            name='ModuleTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
                ('template', models.ForeignKey(to='crowdsourcing.Template')),
            ],
        ),
        migrations.AlterField(
            model_name='templateitem',
            name='template',
            field=models.ForeignKey(related_name='template_items', to='crowdsourcing.Template'),
        ),
        migrations.AlterField(
            model_name='module',
            name='project',
            field=models.ForeignKey(related_name='modules', to='crowdsourcing.Project'),
        ),
        migrations.CreateModel(
            name='BookmarkedProjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile', models.ForeignKey(to='crowdsourcing.UserProfile')),
                ('project', models.ForeignKey(to='crowdsourcing.Project')),
            ],
        ),
        migrations.AddField(
            model_name='module',
            name='template',
            field=models.ManyToManyField(to=b'crowdsourcing.Template', through='crowdsourcing.ModuleTemplate'),
        ),
        migrations.RenameField(
            model_name='modulereview',
            old_name='annonymous',
            new_name='anonymous',
        ),
        migrations.AddField(
            model_name='task',
            name='data',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='module',
            field=models.ForeignKey(related_name='module_tasks', to='crowdsourcing.Module'),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=64)),
                ('body', models.TextField(max_length=8192)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('message', models.ForeignKey(to='crowdsourcing.Message')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='taskworker',
            name='task',
            field=models.ForeignKey(related_name='task_workers', to='crowdsourcing.Task'),
        ),
        migrations.AlterField(
            model_name='taskworkerresult',
            name='task_worker',
            field=models.ForeignKey(related_name='task_worker_results', to='crowdsourcing.TaskWorker'),
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=64)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='message',
            name='subject',
        ),
        migrations.AddField(
            model_name='message',
            name='conversation',
            field=models.ForeignKey(related_name='messages', to='crowdsourcing.Conversation'),
        ),
        migrations.CreateModel(
            name='ConversationRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('conversation', models.ForeignKey(related_name='conversation_recipient', to='crowdsourcing.Conversation')),
                ('recipient', models.ForeignKey(related_name='recipients', to=settings.AUTH_USER_MODEL)),
                ('date_added', models.DateTimeField(default=datetime.datetime(2015, 7, 9, 2, 17, 3, 587241, tzinfo=utc), auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='conversation',
            name='recipients',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='crowdsourcing.ConversationRecipient'),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='sender',
            field=models.ForeignKey(related_name='sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='status',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='projectrequester',
            unique_together=set([('requester', 'project')]),
        ),
        migrations.AlterUniqueTogether(
            name='workerskill',
            unique_together=set([('worker', 'skill')]),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(max_length=128, error_messages={'required': 'Please specify the street name!'}),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=128, error_messages={'required': 'Please enter the category name!'}),
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=64, error_messages={'required': 'Please specify the city!'}),
        ),
        migrations.AlterField(
            model_name='country',
            name='code',
            field=models.CharField(max_length=8, error_messages={'required': 'Please specify the country code!'}),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=64, error_messages={'required': 'Please specify the country!'}),
        ),
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(max_length=64, error_messages={'required': 'Please specify the language!'}),
        ),
        migrations.AlterField(
            model_name='module',
            name='data_set_location',
            field=models.CharField(default='No data set', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=models.TextField(error_messages={'required': 'Please enter the module description!'}),
        ),
        migrations.AlterField(
            model_name='module',
            name='name',
            field=models.CharField(max_length=128, error_messages={'required': 'Please enter the module name!'}),
        ),
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Created'), (2, 'In Review'), (3, 'In Progress'), (4, 'Completed')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.CharField(default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=128, error_messages={'required': 'Please enter the project name!'}),
        ),
        migrations.AlterField(
            model_name='qualification',
            name='type',
            field=models.IntegerField(default=1, choices=[(1, 'Strict'), (2, 'Flexible')]),
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(unique=True, max_length=32, error_messages={'unique': 'The role %(value)r already exists. Please provide another name!', 'required': 'Please specify the role name!'}),
        ),
        migrations.AlterField(
            model_name='skill',
            name='description',
            field=models.CharField(max_length=512, error_messages={'required': 'Please enter the skill description!'}),
        ),
        migrations.AlterField(
            model_name='skill',
            name='name',
            field=models.CharField(max_length=128, error_messages={'required': 'Please enter the skill name!'}),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Created'), (2, 'Accepted'), (3, 'Assigned'), (4, 'Finished')]),
        ),
        migrations.AlterField(
            model_name='taskworkerresult',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Created'), (2, 'Accepted'), (3, 'Rejected')]),
        ),
        migrations.AlterField(
            model_name='template',
            name='name',
            field=models.CharField(max_length=128, error_messages={'required': 'Please enter the template name!'}),
        ),
        migrations.AlterField(
            model_name='templateitem',
            name='name',
            field=models.CharField(max_length=128, error_messages={'required': 'Please enter the name of the template item!'}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='birthday',
            field=models.DateField(null=True, error_messages={'invalid': 'Please enter a correct date format'}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='requester_alias',
            field=models.CharField(max_length=32, error_messages={'required': 'Please enter an alias!'}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='worker_alias',
            field=models.CharField(max_length=32, error_messages={'required': 'Please enter an alias!'}),
        ),
        migrations.AlterUniqueTogether(
            name='projectrequester',
            unique_together=set([('requester', 'project')]),
        ),
        migrations.AlterUniqueTogether(
            name='workerskill',
            unique_together=set([('worker', 'skill')]),
        ),
        migrations.CreateModel(
            name='RequesterInputFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'tmp/')),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='WorkerRequesterRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.IntegerField(default=2, choices=[(1, b'BelowExpectations'), (2, b'MetExpectations'), (3, b'ExceedsExpectations')])),
                ('type', models.CharField(max_length=16)),
                ('origin', models.ForeignKey(related_name='rating_origin', to='crowdsourcing.UserProfile')),
                ('target', models.ForeignKey(related_name='rating_target', to='crowdsourcing.UserProfile')),
                ('created_timestamp', models.DateTimeField(default=datetime.datetime(2015, 8, 14, 20, 8, 53, 936528, tzinfo=utc), auto_now_add=True)),
                ('last_updated', models.DateTimeField(default=datetime.datetime(2015, 8, 14, 20, 9, 0, 336441, tzinfo=utc), auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='requester_alias',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='worker_alias',
        ),
        migrations.AddField(
            model_name='requester',
            name='alias',
            field=models.CharField(default='none', max_length=32, error_messages={b'required': b'Please enter an alias!'}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='worker',
            name='alias',
            field=models.CharField(default='none', max_length=32, error_messages={b'required': b'Please enter an alias!'}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='module',
            name='is_micro',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='taskworker',
            name='task_status',
            field=models.IntegerField(default=1, choices=[(1, b'In Progress'), (2, b'Submitted'), (3, b'Accepted'), (4, b'Rejected'), (5, b'Returned'), (6, b'Skipped')]),
        ),
        migrations.AddField(
            model_name='module',
            name='is_prototype',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='templateitem',
            name='position',
            field=models.IntegerField(),
        ),
        migrations.AddField(
            model_name='workerrequesterrating',
            name='module',
            field=models.ForeignKey(related_name='rating_module', default=1, to='crowdsourcing.Module'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workerrequesterrating',
            name='weight',
            field=models.FloatField(default=2, choices=[(1, b'BelowExpectations'), (2, b'MetExpectations'), (3, b'ExceedsExpectations')]),
        ),
        migrations.AlterField(
            model_name='workerrequesterrating',
            name='weight',
            field=models.FloatField(default=2),
        ),
        migrations.AlterModelOptions(
            name='templateitem',
            options={'ordering': ['position']},
        ),
        migrations.AddField(
            model_name='module',
            name='min_rating',
            field=models.FloatField(default=3.3),
        ),
        migrations.AddField(
            model_name='module',
            name='allow_feedback',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='module',
            name='feedback_permissions',
            field=models.IntegerField(default=1, choices=[(1, b'Others:Read+Write::Workers:Read+Write'), (2, b'Others:Read::Workers:Read+Write'), (3, b'Others:Read::Workers:Read')]),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(max_length=8192)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(related_name='reply_to', to='crowdsourcing.Comment', null=True)),
                ('sender', models.ForeignKey(related_name='comment_sender', to='crowdsourcing.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='ModuleComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(related_name='modulecomment_comment', to='crowdsourcing.Comment')),
                ('module', models.ForeignKey(related_name='modulecomment_module', to='crowdsourcing.Module')),
            ],
        ),
        migrations.CreateModel(
            name='TaskComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(related_name='taskcomment_comment', to='crowdsourcing.Comment')),
                ('task', models.ForeignKey(related_name='taskcomment_task', to='crowdsourcing.Task')),
            ],
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['created_timestamp']},
        ),
        migrations.AlterField(
            model_name='module',
            name='feedback_permissions',
            field=models.IntegerField(default=1, choices=[(1, b'Others:Read+Write::Workers:Read+Write'), (2, b'Others:Read::Workers:Read+Write'), (3, b'Others:Read::Workers:Read'), (4, b'Others:None::Workers:Read')]),
        ),
        migrations.AddField(
            model_name='taskworker',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='module',
            name='min_rating',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='module',
            name='min_rating',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='taskworkerresult',
            name='result',
            field=models.TextField(null=True),
        ),
        migrations.RenameField(
            model_name='workerrequesterrating',
            old_name='type',
            new_name='origin_type',
        ),
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'In Review'), (3, b'In Progress'), (4, b'Completed'), (5, b'Paused')]),
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=models.TextField(max_length=2048, error_messages={b'required': b'Please enter the module description!'}),
        ),
        migrations.AlterIndexTogether(
            name='workerrequesterrating',
            index_together=set([('origin', 'target'), ('origin', 'target', 'created_timestamp', 'origin_type')]),
        ),
        migrations.AlterIndexTogether(
            name='workerrequesterrating',
            index_together=set([('origin', 'target', 'last_updated', 'origin_type'), ('origin', 'target')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_active',
            field=models.DateTimeField(null=True),
        ),
        migrations.RemoveField(
            model_name='templateitem',
            name='sub_type',
        ),
        migrations.AddField(
            model_name='templateitem',
            name='label',
            field=models.TextField(null=True, blank=True),
        ),
    ]
