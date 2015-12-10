from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('crowdsourcing', '0007_auto_20151208_1957'),
    ]

    operations = [
        migrations.RunSQL('''
            create or replace function get_requester_ratings(in worker_profile_id integer)
                returns table(requester_id integer, requester_rating double precision,
                requester_avg_rating double precision)
                AS $$
                select r.id, wr_rating.weight, avg_wr_rating from crowdsourcing_module m
                inner join crowdsourcing_requester r
                on r.id = m.owner_id and m.status=3
                LEFT OUTER JOIN (
                    SELECT wrr.target_id, wrr.weight as weight
                    FROM crowdsourcing_workerrequesterrating wrr
                    INNER JOIN(
                        SELECT target_id, MAX(last_updated) AS max_date
                        FROM crowdsourcing_workerrequesterrating
                        WHERE origin_type='worker' AND origin_id=$1
                        GROUP BY target_id
                    ) most_recent
                    ON wrr.target_id = most_recent.target_id AND wrr.last_updated = most_recent.max_date
                    AND wrr.origin_type='worker' AND wrr.origin_id = $1
                ) wr_rating on wr_rating.target_id = r.profile_id
                LEFT OUTER JOIN (
                    SELECT target_id, AVG(weight) AS avg_wr_rating
                    FROM (
                        SELECT wrr.target_id, wrr.weight
                        FROM crowdsourcing_workerrequesterrating wrr
                        INNER JOIN (
                            SELECT origin_id, target_id, MAX(last_updated) AS max_date
                            FROM crowdsourcing_workerrequesterrating
                            GROUP BY origin_id, target_id
                        ) most_recent
                        ON most_recent.origin_id=wrr.origin_id AND most_recent.target_id=wrr.target_id
                        AND wrr.last_updated=most_recent.max_date
                        AND wrr.origin_id <> $1 AND wrr.origin_type='worker'
                    ) recent_wr_rating
                    GROUP BY target_id
                ) avg_wr_rating
                ON avg_wr_rating.target_id = r.profile_id
                $$
            LANGUAGE SQL
            STABLE
            RETURNS NULL ON NULL INPUT;
        ''')
    ]
