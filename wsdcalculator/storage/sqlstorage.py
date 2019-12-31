import mysql.connector
import os

from .evaluationstorage import EvaluationStorage
from .recordingstorage import FileStorage
from ..models.attempt import Attempt

class SQLStorage(EvaluationStorage, FileStorage):
    def __init__(self):
        p = os.environ.get('MYSQL_PASSWORD', None)
        self.db = mysql.connector.connect(host='localhost', user='root', password=p, database='apraxiator')

    def _add_evaluation(self, e):
        sql = 'INSERT INTO evaluations (evaluation_id, owner_id, ambiance_threshold) VALUES (%s, %s, %s)'
        val = (e.id, e.owner_id, e.ambiance_threshold)
        self._execute_insert_query(sql, val)

    def _get_threshold(self, id):
        sql = 'SELECT * FROM evaluations WHERE evaluation_id = %s'
        val = (id,)
        res = self._execute_select_query(sql, val)
        return res[2]
    
    def _add_attempt(self, a):
        sql = 'INSERT INTO attempts (attempt_id, evaluation_id, term, wsd, duration) VALUE (%s, %s, %s, %s, %s)'
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

    def _get_recording(self, attempt_id):
        sql = 'SELECT recording FROM recordings WHERE attempt_id = %s'
        val = (attempt_id,)
        res = self._execute_select_query(sql, val)
        return res[0]