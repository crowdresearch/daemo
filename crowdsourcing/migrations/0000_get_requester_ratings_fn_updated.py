# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('crowdsourcing', '0007_auto_20151208_1957'),
    ]

    operations = [
        migrations.RunSQL('''
            CREATE OR REPLACE FUNCTION get_requester_ratings(IN worker_profile_id INTEGER)
                RETURNS TABLE(requester_id INTEGER, requester_rating DOUBLE PRECISION,
                requester_avg_rating DOUBLE PRECISION)
                AS $$
                SELECT
                  u.id,
                  wr_rating.weight,
                  avg_wr_rating
                FROM auth_user u
                  LEFT OUTER JOIN (
                                    SELECT
                                      r.target_id,
                                      r.weight AS weight
                                    FROM crowdsourcing_rating r
                                      INNER JOIN (
                                                   SELECT
                                                     target_id,
                                                     MAX(last_updated) AS max_date
                                                   FROM crowdsourcing_rating
                                                   WHERE origin_type = 'worker' AND origin_id = $1
                                                   GROUP BY target_id
                                                 ) most_recent
                                        ON r.target_id = most_recent.target_id AND r.last_updated = most_recent.max_date AND
                                           r.origin_type = 'worker'
                                           AND r.origin_id = $1
                                  ) wr_rating ON wr_rating.target_id = u.id
                  LEFT OUTER JOIN (
                                    SELECT
                                      target_id,
                                      AVG(weight) AS avg_wr_rating
                                    FROM (
                                           SELECT
                                             r.target_id,
                                             r.weight
                                           FROM crowdsourcing_rating r
                                             INNER JOIN (
                                                          SELECT
                                                            origin_id,
                                                            target_id,
                                                            MAX(last_updated) AS max_date
                                                          FROM crowdsourcing_rating
                                                          WHERE origin_id<>$1 AND origin_type='worker'
                                                          GROUP BY origin_id, target_id
                                                        ) most_recent
                                               ON most_recent.origin_id = r.origin_id AND most_recent.target_id = r.target_id AND
                                                  r.last_updated = most_recent.max_date
                                                  AND r.origin_id <> $1 AND r.origin_type = 'worker'
                                         ) recent_wr_rating
                                    GROUP BY target_id
                                  ) avg_wr_rating
                    ON avg_wr_rating.target_id = u.id;
                $$
            LANGUAGE SQL
            STABLE
            RETURNS NULL ON NULL INPUT;
        ''')
    ]
