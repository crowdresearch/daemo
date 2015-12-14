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
                     r.id                                            requester_id,
                     worker_ratings.weight                           weight,
                     CASE WHEN worker_ratings.number_of_ratings = 1
                       THEN CASE WHEN $2 = TRUE
                         THEN worker_ratings.avg_rw_rating
                            ELSE NULL END
                     ELSE (worker_ratings.avg_rw_rating * worker_ratings.number_of_ratings - worker_ratings.weight) /
                          (worker_ratings.number_of_ratings - 1) END average_rating
                   FROM crowdsourcing_requester r LEFT OUTER JOIN (
                                                                    SELECT
                                                                      wrr.target_id,
                                                                      wrr.origin_id,
                                                                      wrr.weight,
                                                                      avg_rw_rating,
                                                                      number_of_ratings
                                                                    FROM crowdsourcing_workerrequesterrating wrr
                                                                      INNER JOIN (
                                                                                   SELECT
                                                                                     recent_req_rating.target_id,
                                                                                     AVG(recent_req_rating.weight) AS avg_rw_rating,
                                                                                     COUNT(
                                                                                         recent_req_rating.target_id) number_of_ratings
                                                                                   FROM (
                                                                                          SELECT
                                                                                            wrr.weight,
                                                                                            wrr.target_id
                                                                                          FROM
                                                                                            crowdsourcing_workerrequesterrating wrr
                                                                                            INNER JOIN (
                                                                                                         SELECT
                                                                                                           origin_id,
                                                                                                           target_id,
                                                                                                           MAX(
                                                                                                               last_updated) AS max_date
                                                                                                         FROM
                                                                                                           crowdsourcing_workerrequesterrating
                                                                                                         WHERE target_id=$1 AND origin_type='requester'
                                                                                                         GROUP BY origin_id,
                                                                                                           target_id
                                                                                                       ) most_recent
                                                                                              ON most_recent.origin_id =
                                                                                                 wrr.origin_id AND
                                                                                                 most_recent.target_id =
                                                                                                 wrr.target_id
                                                                                                 AND
                                                                                                 wrr.last_updated =
                                                                                                 most_recent.max_date
                                                                                                 AND wrr.target_id = $1
                                                                                                 AND wrr.origin_type =
                                                                                                     'requester') recent_req_rating
                                                                                   GROUP BY recent_req_rating.target_id
                                                                                 ) avg_rw_rating
                                                                        ON wrr.target_id = avg_rw_rating.target_id
                                                                      INNER JOIN (
                                                                                   SELECT
                                                                                     origin_id,
                                                                                     target_id,
                                                                                     MAX(last_updated) AS max_date
                                                                                   FROM crowdsourcing_workerrequesterrating
                                                                                   WHERE origin_type='requester'
                                                                                   GROUP BY origin_id, target_id
                                                                                 ) most_recent
                                                                        ON wrr.origin_id = most_recent.origin_id AND
                                                                           wrr.target_id = most_recent.target_id AND
                                                                           wrr.last_updated = most_recent.max_date AND
                                                                           wrr.origin_type = 'requester') worker_ratings
                       ON r.profile_id = worker_ratings.origin_id
            $$
            LANGUAGE SQL
            STABLE
            RETURNS NULL ON NULL INPUT;
        ''')
    ]
