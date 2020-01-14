import pymysql
import os
import logging
import pickle

from .evaluationstorage import EvaluationStorage
from .recordingstorage import RecordingStorage
from ..models.attempt import Attempt
from .dbexceptions import ConnectionException

class SQLStorage(EvaluationStorage, RecordingStorage):
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
        sql = 'INSERT INTO evaluations (evaluation_id, owner_id, ambience_threshold) VALUES (%s, %s, %s)'
        self.logger.info(e.id)
        val = (e.id, e.owner_id, e.ambiance_threshold)
        self._execute_insert_query(sql, val)

    def _get_threshold(self, id):
        sql = 'SELECT * FROM evaluations WHERE evaluation_id = %s'
        val = (id,)
        res = self._execute_select_query(sql, val)
        return res[2]
    
    def _add_attempt(self, a):
        sql = 'INSERT INTO attempts (attempt_id, evaluation_id, word, wsd, duration) VALUE (%s, %s, %s, %s, %s)'
        val = (a.id, a.evaluation_id, a.term, a.wsd, a.duration)
        self._execute_insert_query(sql, val)

    def _get_attempts(self, evaluation_id):
        sql = 'SELECT * FROM attempts WHERE evaluation_id = %s'
        val = (evaluation_id,)
        res = self._execute_select_many_query(sql, val)
        attempts = []
        for row in res:
            attempts.append(*row)
        return attempts

    def _check_is_owner(self, evaluation_id, owner_id):
        return True

    def _execute_insert_query(self, sql, val):
        c = self.db.cursor()
        c.execute(sql, val)
        self.db.commit()
    
    def _execute_select_query(self, sql, val):
        c = self.db.cursor()
        c.execute(sql, val)
        return c.fetchone()

    def _execute_select_many_query(self, sql, val):
        c = self.db.cursor()
        c.execute(sql, val)
        return c.fetchall()

    def _save_recording(self, recording, attempt_id):
        sql = 'INSERT INTO recordings (attempt_id, recording) VALUE (%s, %s)'
        val = (attempt_id, recording)
        self._execute_insert_query(sql, val)
        return attempt_id

    def _get_recording(self, attempt_id):
        sql = 'SELECT recording FROM recordings WHERE attempt_id = %s'
        val = (attempt_id,)
        res = self._execute_select_query(sql, val)
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