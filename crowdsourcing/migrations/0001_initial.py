# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import oauth2client.django_orm


class Migration(migrations.Migration):

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
            name='BookmarkedProjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(max_length=8192)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(related_name='reply_to', to='crowdsourcing.Comment', null=True)),
            ],
            options={
                'ordering': ['created_timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=64)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ConversationRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(related_name='conversation_recipient', to='crowdsourcing.Conversation')),
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
            name='FinancialAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'general', max_length=16)),
                ('is_active', models.BooleanField(default=True)),
                ('balance', models.FloatField(default=0)),
                ('is_system', models.BooleanField(default=False)),
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
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(max_length=8192)),
                ('deleted', models.BooleanField(default=False)),
                ('status', models.IntegerField(default=1)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('conversation', models.ForeignKey(related_name='messages', to='crowdsourcing.Conversation')),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, error_messages={b'required': b'Please enter the module name!'})),
                ('description', models.TextField(max_length=2048, error_messages={b'required': b'Please enter the module description!'})),
                ('keywords', models.TextField(null=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'In Review'), (3, b'In Progress'), (4, b'Completed'), (5, b'Paused')])),
                ('price', models.FloatField()),
                ('repetition', models.IntegerField(default=1)),
                ('module_timeout', models.IntegerField(default=0)),
                ('has_data_set', models.BooleanField(default=False)),
                ('data_set_location', models.CharField(default=b'No data set', max_length=256, null=True)),
                ('task_time', models.FloatField(default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('is_micro', models.BooleanField(default=True)),
                ('is_prototype', models.BooleanField(default=False)),
                ('min_rating', models.FloatField(default=0)),
                ('allow_feedback', models.BooleanField(default=True)),
                ('feedback_permissions', models.IntegerField(default=1, choices=[(1, b'Others:Read+Write::Workers:Read+Write'), (2, b'Others:Read::Workers:Read+Write'), (3, b'Others:Read::Workers:Read'), (4, b'Others:None::Workers:Read')])),
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
            name='ModuleComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(related_name='modulecomment_comment', to='crowdsourcing.Comment')),
                ('module', models.ForeignKey(related_name='modulecomment_module', to='crowdsourcing.Module')),
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
                ('anonymous', models.BooleanField(default=False)),
                ('comments', models.TextField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
            ],
        ),
        migrations.CreateModel(
            name='ModuleTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
            name='PayPalFlow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('paypal_id', models.CharField(max_length=128)),
                ('state', models.CharField(default=b'created', max_length=16)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('redirect_url', models.CharField(max_length=256)),
                ('payer_id', models.CharField(max_length=64, null=True)),
                ('recipient', models.ForeignKey(related_name='flow_recipient', to='crowdsourcing.FinancialAccount')),
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
                ('keywords', models.TextField(null=True)),
                ('save_to_drive', models.BooleanField(default=False)),
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
                ('name', models.CharField(max_length=64, error_messages={b'required': b'Please specify the region!'})),
                ('code', models.CharField(max_length=16, error_messages={b'required': b'Please specify the region code!'})),
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
                ('alias', models.CharField(max_length=32, error_messages={b'required': b'Please enter an alias!'})),
            ],
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
                ('data', models.TextField(null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('price', models.FloatField(default=0)),
                ('module', models.ForeignKey(related_name='module_tasks', to='crowdsourcing.Module')),
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
        migrations.CreateModel(
            name='TaskWorker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_status', models.IntegerField(default=1, choices=[(1, b'In Progress'), (2, b'Submitted'), (3, b'Accepted'), (4, b'Rejected'), (5, b'Returned'), (6, b'Skipped')])),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('task', models.ForeignKey(related_name='task_workers', to='crowdsourcing.Task')),
            ],
        ),
        migrations.CreateModel(
            name='TaskWorkerResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.TextField(null=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'Accepted'), (3, b'Rejected')])),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('task_worker', models.ForeignKey(related_name='task_worker_results', to='crowdsourcing.TaskWorker')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, error_messages={b'required': b'Please enter the template name!'})),
                ('source_html', models.TextField(default=None, null=True)),
                ('price', models.FloatField(default=0)),
                ('share_with_others', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemplateItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, error_messages={b'required': b'Please enter the name of the template item!'})),
                ('id_string', models.CharField(max_length=128)),
                ('role', models.CharField(max_length=16)),
                ('icon', models.CharField(max_length=256, null=True)),
                ('data_source', models.CharField(max_length=256, null=True)),
                ('layout', models.CharField(default=b'column', max_length=16)),
                ('type', models.CharField(max_length=16)),
                ('sub_type', models.CharField(max_length=16)),
                ('values', models.TextField(null=True)),
                ('position', models.IntegerField()),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('template', models.ForeignKey(related_name='template_items', to='crowdsourcing.Template')),
            ],
            options={
                'ordering': ['position'],
            },
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
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.FloatField()),
                ('state', models.CharField(default=b'created', max_length=16)),
                ('method', models.CharField(default=b'paypal', max_length=16)),
                ('sender_type', models.CharField(default=b'self', max_length=8)),
                ('reference', models.CharField(max_length=256, null=True)),
                ('currency', models.CharField(default=b'USD', max_length=4)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('recipient', models.ForeignKey(related_name='transaction_recipient', to='crowdsourcing.FinancialAccount')),
                ('sender', models.ForeignKey(related_name='transaction_sender', to='crowdsourcing.FinancialAccount')),
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
            name='UserMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('message', models.ForeignKey(to='crowdsourcing.Message')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
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
                ('last_active', models.DateTimeField(null=True)),
                ('address', models.ForeignKey(to='crowdsourcing.Address', null=True)),
                ('friends', models.ManyToManyField(to='crowdsourcing.UserProfile', through='crowdsourcing.Friendship')),
                ('languages', models.ManyToManyField(to='crowdsourcing.Language', through='crowdsourcing.UserLanguage')),
                ('nationality', models.ManyToManyField(to='crowdsourcing.Country', through='crowdsourcing.UserCountry')),
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
                ('alias', models.CharField(max_length=32, error_messages={b'required': b'Please enter an alias!'})),
                ('profile', models.OneToOneField(to='crowdsourcing.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='WorkerModuleApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'Accepted'), (3, b'Rejected')])),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
                ('worker', models.ForeignKey(to='crowdsourcing.Worker')),
            ],
        ),
        migrations.CreateModel(
            name='WorkerRequesterRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.FloatField(default=2)),
                ('origin_type', models.CharField(max_length=16)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(related_name='rating_module', to='crowdsourcing.Module')),
                ('origin', models.ForeignKey(related_name='rating_origin', to='crowdsourcing.UserProfile')),
                ('target', models.ForeignKey(related_name='rating_target', to='crowdsourcing.UserProfile')),
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
            field=models.ManyToManyField(to='crowdsourcing.Skill', through='crowdsourcing.WorkerSkill'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='roles',
            field=models.ManyToManyField(to='crowdsourcing.Role', through='crowdsourcing.UserRole'),
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
            model_name='template',
            name='owner',
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
            field=models.ManyToManyField(to='crowdsourcing.Category', through='crowdsourcing.ProjectCategory'),
        ),
        migrations.AddField(
            model_name='project',
            name='collaborators',
            field=models.ManyToManyField(to='crowdsourcing.Requester', through='crowdsourcing.ProjectRequester'),
        ),
        migrations.AddField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(related_name='project_owner', to='crowdsourcing.Requester'),
        ),
        migrations.AddField(
            model_name='moduletemplate',
            name='template',
            field=models.ForeignKey(to='crowdsourcing.Template'),
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
            field=models.ManyToManyField(to='crowdsourcing.Category', through='crowdsourcing.ModuleCategory'),
        ),
        migrations.AddField(
            model_name='module',
            name='owner',
            field=models.ForeignKey(to='crowdsourcing.Requester'),
        ),
        migrations.AddField(
            model_name='module',
            name='project',
            field=models.ForeignKey(related_name='modules', to='crowdsourcing.Project'),
        ),
        migrations.AddField(
            model_name='module',
            name='template',
            field=models.ManyToManyField(to='crowdsourcing.Template', through='crowdsourcing.ModuleTemplate'),
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
            model_name='financialaccount',
            name='owner',
            field=models.ForeignKey(related_name='account_owner', to='crowdsourcing.UserProfile', null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='region',
            field=models.ForeignKey(to='crowdsourcing.Region'),
        ),
        migrations.AddField(
            model_name='conversationrecipient',
            name='recipient',
            field=models.ForeignKey(related_name='recipients', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conversation',
            name='recipients',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='crowdsourcing.ConversationRecipient'),
        ),
        migrations.AddField(
            model_name='conversation',
            name='sender',
            field=models.ForeignKey(related_name='sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='sender',
            field=models.ForeignKey(related_name='comment_sender', to='crowdsourcing.UserProfile'),
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(to='crowdsourcing.Country'),
        ),
        migrations.AddField(
            model_name='bookmarkedprojects',
            name='profile',
            field=models.ForeignKey(to='crowdsourcing.UserProfile'),
        ),
        migrations.AddField(
            model_name='bookmarkedprojects',
            name='project',
            field=models.ForeignKey(to='crowdsourcing.Project'),
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
            name='workerskill',
            unique_together=set([('worker', 'skill')]),
        ),
        migrations.AlterIndexTogether(
            name='workerrequesterrating',
            index_together=set([('origin', 'target', 'last_updated', 'origin_type'), ('origin', 'target')]),
        ),
        migrations.AlterUniqueTogether(
            name='projectrequester',
            unique_together=set([('requester', 'project')]),
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
    ]
