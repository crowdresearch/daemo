# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('crowdsourcing', '0000_get_min_ratings_fn'),
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
                                                     MAX(updated_at) AS max_date
                                                   FROM crowdsourcing_rating
                                                   WHERE origin_type = 1 AND origin_id = $1
                                                   GROUP BY target_id
                                                 ) most_recent
                                        ON r.target_id = most_recent.target_id AND r.updated_at = most_recent.max_date AND
                                           r.origin_type = 1
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
                                                            MAX(updated_at) AS max_date
                                                          FROM crowdsourcing_rating
                                                          WHERE origin_id<>$1 AND origin_type=1
                                                          GROUP BY origin_id, target_id
                                                        ) most_recent
                                               ON most_recent.origin_id = r.origin_id AND most_recent.target_id = r.target_id AND
                                                  r.updated_at = most_recent.max_date
                                                  AND r.origin_id <> $1 AND r.origin_type = 1
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
