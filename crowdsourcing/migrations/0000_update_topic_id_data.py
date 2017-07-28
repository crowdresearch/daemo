from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations

from crowdsourcing.discourse import DiscourseClient
from crowdsourcing.utils import get_trailing_number


def update_topic_id_data(apps, schema_editor):
    # We can't import the Project model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    project_model = apps.get_model("crowdsourcing", "Project")
    projects = project_model.objects.all()

    client = DiscourseClient(
        settings.DISCOURSE_BASE_URL,
        api_username='system',
        api_key=settings.DISCOURSE_API_KEY)

    for project in projects:
        if project.discussion_link is not None:
            topic_id = get_trailing_number(project.discussion_link)

            if topic_id is not None and project.topic_id < 0:
                project.topic_id = topic_id
                project.save()

                try:
                    if project.post_id < 0:
                        posts = client.posts(topic_id)

                        if 'post_stream' in posts and 'stream' in posts['post_stream'] \
                                and posts['post_stream']['stream'] is not None:

                                post_id = posts['post_stream']['stream'][0]
                                if post_id is not None and post_id > 0:
                                    project.post_id = post_id
                                    project.save()
                except Exception as e:
                    print e


class Migration(migrations.Migration):
    dependencies = [
        ('crowdsourcing', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_topic_id_data),
    ]
