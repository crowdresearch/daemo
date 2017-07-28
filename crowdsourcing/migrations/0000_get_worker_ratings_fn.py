# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('crowdsourcing', '0000_get_requester_ratings_fn'),
    ]

    operations = [
        migrations.RunSQL('''
            CREATE OR REPLACE FUNCTION get_worker_ratings(IN worker_profile_id INTEGER, IN true_avg BOOLEAN DEFAULT FALSE)
  RETURNS TABLE(requester_id INTEGER, worker_rating DOUBLE PRECISION,
  worker_avg_rating DOUBLE PRECISION)
AS $$
SELECT
  u.id                                            requester_id,
  worker_ratings.weight                           weight,
  CASE WHEN worker_ratings.number_of_ratings = 1
    THEN CASE WHEN $2 = TRUE
      THEN worker_ratings.avg_rw_rating
         ELSE NULL END
  ELSE (worker_ratings.avg_rw_rating * worker_ratings.number_of_ratings - worker_ratings.weight) /
       (worker_ratings.number_of_ratings - 1) END average_rating
FROM auth_user u
  LEFT OUTER JOIN (
                    SELECT
                      r.target_id,
                      r.origin_id,
                      r.weight,
                      avg_rw_rating,
                      number_of_ratings
                    FROM crowdsourcing_rating r
                      INNER JOIN (
                                   SELECT
                                     recent_req_rating.target_id,
                                     AVG(recent_req_rating.weight) AS avg_rw_rating,
                                     COUNT(
                                         recent_req_rating.target_id) number_of_ratings
                                   FROM (
                                          SELECT
                                            r.weight,
                                            r.target_id
                                          FROM
                                            crowdsourcing_rating r
                                            INNER JOIN (
                                                         SELECT
                                                           origin_id,
                                                           target_id,
                                                           MAX(
                                                               updated_at) AS max_date
                                                         FROM
                                                           crowdsourcing_rating
                                                         WHERE target_id = $1 AND
                                                               origin_type = 2
                                                         GROUP BY origin_id,
                                                           target_id
                                                       ) most_recent
                                              ON most_recent.origin_id =
                                                 r.origin_id AND
                                                 most_recent.target_id =
                                                 r.target_id
                                                 AND
                                                 r.updated_at =
                                                 most_recent.max_date
                                                 AND r.target_id = $1
                                                 AND r.origin_type =
                                                     2) recent_req_rating
                                   GROUP BY recent_req_rating.target_id
                                 ) avg_rw_rating
                        ON r.target_id = avg_rw_rating.target_id
                      INNER JOIN (
                                   SELECT
                                     origin_id,
                                     target_id,
                                     MAX(updated_at) AS max_date
                                   FROM crowdsourcing_rating
                                   WHERE origin_type = 2
                                   GROUP BY origin_id, target_id
                                 ) most_recent
                        ON r.origin_id = most_recent.origin_id AND
                           r.target_id = most_recent.target_id AND
                           r.updated_at = most_recent.max_date AND
                           r.origin_type = 2) worker_ratings
    ON u.id = worker_ratings.origin_id
$$
LANGUAGE SQL
STABLE
RETURNS NULL ON NULL INPUT;
        ''')
    ]
