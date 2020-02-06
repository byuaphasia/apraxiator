import pymysql
import os
import logging
import pickle

from .evaluationstorage import EvaluationStorage
from .recordingstorage import RecordingStorage
from .waiverstorage import WaiverStorage
from ..models.waiver import Waiver
from ..models.attempt import Attempt
from .dbexceptions import ConnectionException, ResourceAccessException
from .storageexceptions import PermissionDeniedException

class SQLStorage(EvaluationStorage, RecordingStorage, WaiverStorage):
    def __init__(self):
        p = os.environ.get('MYSQL_PASSWORD', None)
        self.db = pymysql.connections.Connection(user='root', password=p, database='apraxiator')
        self.logger = logging.getLogger(__name__)
        self._create_tables()
        self.logger.info('[event=sql-storage-started]')

    def is_healthy(self):
        try:
            self.db.ping()
        except Exception as e:
            self.logger.exception('[event=ping-db-error]')
            raise ConnectionException(e)

    def _add_evaluation(self, e):
        sql = 'INSERT INTO evaluations (evaluation_id, owner_id, ambiance_threshold) VALUES (%s, %s, %s)'
        val = (e.id, e.owner_id, e.ambiance_threshold)
        try:
            self._execute_insert_query(sql, val)
        except Exception as ex:
            self.logger.exception('[event=add-evaluation-failure][evaluationId=%s]', e.id)
            raise ResourceAccessException(e.id, ex)
        self.logger.info('[event=evaluation-added][evaluationId=%s]', e.id)

    def _get_threshold(self, id):
        sql = 'SELECT ambiance_threshold FROM evaluations WHERE evaluation_id = %s'
        val = (id,)
        try:
            res = self._execute_select_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=get-threshold-failure][evaluationId=%s]', id)
            raise ResourceAccessException(id, e)
        self.logger.info('[event=threshold-retrieved][evaluationId=%s][threshold=%s]', id, res[0])
        return res[0]
    
    def _add_attempt(self, a):
        sql = 'INSERT INTO attempts (attempt_id, evaluation_id, word, wsd, duration) VALUE (%s, %s, %s, %s, %s)'
        val = (a.id, a.evaluation_id, a.word, a.wsd, a.duration)
        try:
            self._execute_insert_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=add-attempt-failure][evaluationId=%s][attemptId=%s]', a.evaluation_id, a.id)
            raise ResourceAccessException(a.id, e)
        self.logger.info('[event=attempt-added][evaluationId=%s][attemptId=%s]', a.evaluation_id, a.id)

    def _get_attempts(self, evaluation_id):
        sql = 'SELECT * FROM attempts WHERE evaluation_id = %s'
        val = (evaluation_id,)
        try:
            res = self._execute_select_many_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=get-attempts-failure][evaluationId=%s]', evaluation_id)
            raise ResourceAccessException(evaluation_id, e)
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

    def _execute_update_statement(self, sql, val):
        self.logger.info(self._make_info_log('db-update', sql, val))
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
        try:
            self._execute_insert_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=save-recording-failure][attemptId=%s]', attempt_id)
            raise ResourceAccessException(attempt_id, e)
        self.logger.info('[event=recording-saved][attemptId=%s]', attempt_id)

    def _get_recording(self, attempt_id):
        sql = 'SELECT recording FROM recordings WHERE attempt_id = %s'
        val = (attempt_id,)
        try:
            res = self._execute_select_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=get-recording-failure][attemptId=%s]', attempt_id)
            raise ResourceAccessException(attempt_id, e)
        self.logger.info('[event=recording-retrieved][attemptId=%s]', attempt_id)
        return res[0]

    def _add_waiver(self, w):
        sql = ("INSERT INTO waivers ("
                "subject_name, subject_email, representative_name, representative_relationship,"
                "signed_on, signer, valid, filepath) "
                "VALUES (%s, %s, %s, %s, %s, %s, %r, %s);")
        val = (w.res_name, w.res_email, w.rep_name, w.rep_relationship, w.date, w.signer, w.valid, w.filepath)
        try:
            self._execute_insert_query(sql, val)
        except Exception as ex:
            self.logger.exception('[event=add-waiver-failure][subjectName=%s][subjectEmail=%s]', w.res_name, w.res_email)
            raise ResourceAccessException(None, ex)
        self.logger.info('[event=waiver-added][subjectName=%s][subjectEmail=%s]', w.res_name, w.res_email)

    def get_valid_waivers(self, res_name, res_email):
        sql = 'SELECT * FROM waivers WHERE subject_name = %s AND subject_email = %s AND valid = %r;'
        val = (res_name, res_email, True)
        try:
            res = self._execute_select_many_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=get-valid-waiver-failure][subjectName=%s][subjectEmail=%s]', res_name, res_email)
            raise ResourceAccessException(None, e)
        waivers = []
        for row in res:
            waivers.append(Waiver.from_row(row))
        self.logger.info('[event=valid-waivers-retrieved][subjectName=%s][subjectEmail=%s][waiverCount=%s]', res_name, res_email, len(waivers))
        return waivers

    def _update_waiver(self, id, field, value):
        sql = 'UPDATE waivers SET {} = %s WHERE waiver_id = %s;'.format(field)
        val = (value, id)
        try:
            self._execute_update_statement(sql, val)
        except Exception as e:
            self.logger.exception('[event=update-waiver-failure][waiverId=%s][field=%s][value=%r]',
                                  id, field, value)
            raise ResourceAccessException(None, e)
        self.logger.info('[event=update-waiver][waiverId=%s][field=%s][value=%r]',
                         id, field, value)

    def _create_tables(self):
        create_evaluations_statement = ("CREATE TABLE IF NOT EXISTS `evaluations` ("
            "`evaluation_id` varchar(48) NOT NULL,"
            "`owner_id` varchar(48) NOT NULL,"
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
        create_waivers_statement = ("CREATE TABLE IF NOT EXISTS `waivers` ("
            "`waiver_id` int AUTO_INCREMENT NOT NULL,"
            "`subject_name` varchar(255) NOT NULL,"
            "`subject_email` varchar(255) NOT NULL,"
            "`representative_name` varchar(255),"
            "`representative_relationship` varchar(255),"
            "`signed_on` varchar(255) NOT NULL,"
            "`signer` varchar(48) NOT NULL,"
            "`valid` boolean NOT NULL DEFAULT TRUE,"
            "`filepath` varchar(255) NOT NULL,"
            "PRIMARY KEY (`waiver_id`)"
            ");"
        )
        c = self.db.cursor()
        c.execute(create_evaluations_statement)
        c.execute(create_attempts_statement)
        c.execute(create_recordings_statement)
        c.execute(create_waivers_statement)

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