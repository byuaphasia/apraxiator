import pymysql
import os
import logging
import pickle

from .evaluationstorage import EvaluationStorage
from .recordingstorage import RecordingStorage
from ..models.attempt import Attempt
from .dbexceptions import ConnectionException
from .storageexceptions import PermissionDeniedException

class SQLStorage(EvaluationStorage):
    def __init__(self):
        p = os.environ.get('MYSQL_PASSWORD', None)
        self.db = pymysql.connections.Connection(user='root', password=p, database='apraxiator')
        self.logger = logging.getLogger(__name__)
        self._create_tables()

    def is_healthy(self):
        try:
            self.db.ping()
        except Exception as e:
            self.logger.exception('[event=ping-db-error]')
            raise ConnectionException(e)

    def _add_evaluation(self, e):
        sql = 'INSERT INTO evaluations (evaluation_id, owner_id, ambiance_threshold) VALUES (%s, %s, %s)'
        val = (e.id, e.owner_id, e.ambiance_threshold)
        self._execute_insert_query(sql, val)
        self.logger.info('[event=evaluation-added][evaluationId=%s]', e.id)

    def _get_threshold(self, id):
        sql = 'SELECT ambiance_threshold FROM evaluations WHERE evaluation_id = %s'
        val = (id,)
        res = self._execute_select_query(sql, val)
        self.logger.info('[event=threshold-retrieved][evaluationId=%s][threshold=%s]', id, res[0])
        return res[0]
    
    def _add_attempt(self, a):
        sql = 'INSERT INTO attempts (attempt_id, evaluation_id, word, wsd, duration) VALUE (%s, %s, %s, %s, %s)'
        val = (a.id, a.evaluation_id, a.word, a.wsd, a.duration)
        self._execute_insert_query(sql, val)
        self.logger.info('[event=attempt-added][evaluationId=%s][attemptId=%s]', a.evaluation_id, a.id)

    def _get_attempts(self, evaluation_id):
        sql = 'SELECT * FROM attempts WHERE evaluation_id = %s'
        val = (evaluation_id,)
        res = self._execute_select_many_query(sql, val)
        attempts = []
        for row in res:
            attempts.append(Attempt.from_row(row))
        self.logger.info('[event=attempts-retrieved][evaluationId=%s][attemptCount=%s]', evaluation_id, len(attempts))
        return attempts

    def _check_is_owner(self, evaluation_id, owner_id):
        sql = 'SELECT owner_id FROM evaluations WHERE evaluation_id = %s'
        val = (evaluation_id,)
        res = self._execute_select_query(sql, val)
        if res[0] != owner_id:
            self.logger.error('[event=access-denied][evaluationId=%s][userId=%s]', evaluation_id, owner_id)
            raise PermissionDeniedException(evaluation_id, owner_id)
        else:
            self.logger.info('[event=owner-verified][evaluationId=%s][userId=%s]', evaluation_id, owner_id)

    def _execute_insert_query(self, sql, val):
        self.logger.info(self._make_info_log('db-insert', sql, val))
        c = self.db.cursor()
        c.execute(sql, val)
        self.db.commit()
    
    def _execute_select_query(self, sql, val):
        self.logger.info(self._make_info_log('db-select', sql, val))
        c = self.db.cursor()
        c.execute(sql, val)
        return c.fetchone()

    def _execute_select_many_query(self, sql, val):
        self.logger.info(self._make_info_log('db-select-many', sql, val))
        c = self.db.cursor()
        c.execute(sql, val)
        return c.fetchall()

    def _save_recording(self, recording, attempt_id):
        sql = 'INSERT INTO recordings (attempt_id, recording) VALUE (%s, %s)'
        val = (attempt_id, recording)
        self._execute_insert_query(sql, val)
        self.logger.info('[event=recording-saved][attemptId=%s]', attempt_id)

    def _get_recording(self, attempt_id):
        sql = 'SELECT recording FROM recordings WHERE attempt_id = %s'
        val = (attempt_id,)
        res = self._execute_select_query(sql, val)
        self.logger.info('[event=recording-retrieved][attemptId=%s]', attempt_id)
        print(res[0])
        return res[0]

    def _create_tables(self):
        create_evaluations_statement = ("CREATE TABLE IF NOT EXISTS `evaluations` ("
            "`evaluation_id` varchar(36) NOT NULL,"
            "`owner_id` varchar(36) NOT NULL,"
            "`ambiance_threshold` float DEFAULT NULL,"
            "`date_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "PRIMARY KEY (`evaluation_id`)"
            ");"
        )
        create_attempts_statement = ("CREATE TABLE IF NOT EXISTS `attempts` ("
            "`evaluation_id` varchar(48) NOT NULL,"
            "`word` varchar(48) NOT NULL,"
            "`attempt_id` varchar(48) NOT NULL,"
            "`wsd` float NOT NULL,"
            "`duration` float NOT NULL,"
            "`date_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "PRIMARY KEY (`attempt_id`),"
            "KEY `evaluation_id_idx` (`evaluation_id`),"
            "CONSTRAINT `evaluation_id` FOREIGN KEY (`evaluation_id`) REFERENCES `evaluations` (`evaluation_id`)"
            ");"
        )
        create_recordings_statement = ("CREATE TABLE IF NOT EXISTS `recordings` ("
            "`recording_id` int AUTO_INCREMENT NOT NULL,"
            "`attempt_id` varchar(48) NOT NULL,"
            "`date_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "`recording` mediumblob NOT NULL,"
            "PRIMARY KEY (`recording_id`),"
            "KEY `attempt_id_idx` (`attempt_id`),"
            "CONSTRAINT `attempt_id` FOREIGN KEY (`attempt_id`) REFERENCES `attempts` (`attempt_id`)"
            ");"
        )
        c = self.db.cursor()
        c.execute(create_evaluations_statement)
        c.execute(create_attempts_statement)
        c.execute(create_recordings_statement)

    @staticmethod
    def _make_info_log(event, sql, val):
        fmt = '[event={event}][sql={sql}][vals={vals}]'

        str_vals = []
        for v in val:
            if isinstance(v, str):
                str_vals.append(v)
            else:
                str_vals.append('nonstring')

        if sql[0] == 'I':
            sql_msg = sql.split('VALUE', 0)[0]
        elif sql[0] == 'S':
            sql_msg = sql.split('=', 0)[0]
        else:
            sql_msg = 'unrecognized sql'
        return fmt.format(event=event, sql=sql_msg, vals='-'.join(str_vals))