# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('crowdsourcing', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            CREATE OR REPLACE FUNCTION is_worker_qualified(expressions IN JSON, worker_data IN JSON)
              RETURNS BOOLEAN
            AS $$
            DECLARE
              item   JSON;
              passed BOOL := TRUE;
            BEGIN
              IF expressions IS NULL
              THEN
                RETURN TRUE;
              END IF;

              FOR item IN SELECT *
                          FROM json_array_elements(expressions)
              LOOP
                DECLARE op     VARCHAR(16);
                        attrib VARCHAR(32);
                BEGIN
                  op := item ->> 'operator';
                  attrib := item ->> 'attribute';
                  IF upper(op) = 'EQ'
                  THEN
                    IF NOT (worker_data ->> attrib = item ->> 'value') OR worker_data ->> attrib IS NULL
                    THEN
                      passed:=FALSE;
                    END IF;
                  ELSIF upper(op) = 'NOT_EQ' OR upper(op) = 'NOTEQ'
                    THEN
                      IF NOT (worker_data ->> attrib <> item ->> 'value') OR worker_data ->> attrib IS NULL
                      THEN
                        passed := FALSE;
                      END IF;
                  ELSIF upper(op) = 'GT'
                    THEN
                      IF NOT (worker_data ->> attrib > item ->> 'value') OR worker_data ->> attrib IS NULL
                      THEN
                        passed := FALSE;
                      END IF;
                  ELSIF upper(op) = 'GTEQ'
                    THEN
                      IF NOT (worker_data ->> attrib >= item ->> 'value') OR worker_data ->> attrib IS NULL
                      THEN
                        passed := FALSE;
                      END IF;
                  ELSIF upper(op) = 'LT'
                    THEN
                      IF NOT (worker_data ->> attrib < item ->> 'value') OR worker_data ->> attrib IS NULL
                      THEN
                        passed := FALSE;
                      END IF;
                  ELSIF upper(op) = 'LTEQ'
                    THEN
                      IF NOT (worker_data ->> attrib <= item ->> 'value' OR worker_data ->> attrib IS NULL)
                      THEN
                        passed := FALSE;
                      END IF;
                  ELSIF upper(op) = 'IN'
                    THEN
                      IF NOT (worker_data ->> attrib IN (SELECT *
                                                         FROM json_array_elements_text(item -> 'value')))
                         OR worker_data ->> attrib IS NULL
                      THEN
                        passed := FALSE;
                      END IF;
                  ELSIF upper(op) = 'NOT_IN' OR upper(op) = 'NOTIN'
                    THEN
                      IF NOT (worker_data ->> attrib NOT IN (SELECT *
                                                             FROM
                                                               json_array_elements_text(item -> 'value')))
                         OR worker_data ->> attrib IS NULL
                      THEN
                        passed := FALSE;
                      END IF;
                  ELSIF upper(op) = 'BETWEEN'
                    THEN
                      IF NOT (
                        worker_data ->> attrib >= item ->> 'value'
                                                           AND worker_data ->> attrib <= item ->> 'value2')
                         OR worker_data ->> attrib IS NULL
                      THEN
                        passed := FALSE;
                      END IF;
                  ELSIF upper(op) = 'CONTAINS'
                    THEN
                      IF NOT (item ->> 'value' IN (SELECT *
                                                         FROM json_array_elements_text(worker_data -> attrib)))
                         OR worker_data ->> attrib IS NULL
                      THEN
                        passed := FALSE;
                      END IF;
                  END IF;
                END;
              END LOOP;
              RETURN passed;
            END;
            $$
            LANGUAGE plpgsql;
        ''')
    ]
