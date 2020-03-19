import pymysql
from pymysql.err import OperationalError
import os
import logging

from src.services.evaluation.ievaluationstorage import IEvaluationStorage
from src.services.waiver.iwaiverstorage import IWaiverStorage
from src.services.dataexport.idataexportstorage import IDataExportStorage
from src.models.evaluation import Evaluation
from src.models.waiver import Waiver
from src.models.attempt import Attempt
from src.storage.dbexceptions import ConnectionException, ResourceAccessException
from src.storage.storageexceptions import PermissionDeniedException, ResourceNotFoundException


class SQLStorage(IEvaluationStorage, IWaiverStorage, IDataExportStorage):
    def __init__(self, name='apraxiator'):
        try:
            host = os.environ.get('APX_MYSQL_HOST', 'localhost')
            u = os.environ['APX_MYSQL_USER']
            if host != 'localhost':
                p = self.get_rds_password(host, u)
            else:
                p = os.environ['APX_MYSQL_PASSWORD']
            self.db = pymysql.connections.Connection(host=host, user=u, password=p, database=name)
            self.logger = logging.getLogger(__name__)
            self._create_tables()
            self.logger.info('[event=sql-storage-started]')
        except KeyError as e:
            raise ConnectionException(e)
        except OperationalError as e:
            raise ConnectionException(e)

    def is_healthy(self):
        try:
            self.db.ping()
        except Exception as e:
            self.logger.exception('[event=ping-db-error]')
            raise ConnectionException(e)

    ''' Evaluation Storage Methods '''

    def create_evaluation(self, e):
        sql = 'INSERT INTO evaluations (evaluation_id, age, gender, impression, owner_id) VALUES (%s, %s, %s, %s, %s)'
        val = (e.id, e.age, e.gender, e.impression, e.owner_id)
        try:
            self._execute_insert_query(sql, val)
        except Exception as ex:
            self.logger.exception('[event=add-evaluation-failure][evaluationId=%s]', e.id)
            raise ResourceAccessException(e.id, ex)
        self.logger.info('[event=evaluation-added][evaluationId=%s]', e.id)

    def update_evaluation(self, id, field, value):
        sql = 'UPDATE evaluations SET {} = %s WHERE evaluation_id = %s'.format(field)
        val = (value, id)
        try:
            self._execute_update_statement(sql, val)
        except Exception as e:
            self.logger.exception('[event=update-evaluation-failure][evaluationId=%s][updateField=%s][updateValue=%r]', id, field, value)
            raise ResourceAccessException(id, e)
        self.logger.info('[event=evaluation-updated][evaluationId=%s][updateField=%s][updateValue=%r]', id, field, value)

    def get_evaluation(self, id):
        sql = 'SELECT * FROM evaluations WHERE evaluation_id = %s'
        val = (id,)
        try:
            res = self._execute_select_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=get-evaluation-failure][evaluationId=%s]', id)
            raise ResourceAccessException(id, e)
        if res is None:
            raise ResourceNotFoundException(id)
        self.logger.info('[event=evaluation-retrieved][evaluationId=%s]', id)
        evaluation = Evaluation.from_row(res)
        return evaluation
    
    def create_attempt(self, a):
        sql = 'INSERT INTO attempts (attempt_id, evaluation_id, word, wsd, duration, syllable_count) VALUE (%s, %s, %s, %s, %s, %s)'
        val = (a.id, a.evaluation_id, a.word, a.wsd, a.duration, a.syllable_count)
        try:
            self._execute_insert_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=add-attempt-failure][evaluationId=%s][attemptId=%s]', a.evaluation_id, a.id)
            raise ResourceAccessException(a.id, e)
        self.logger.info('[event=attempt-added][evaluationId=%s][attemptId=%s]', a.evaluation_id, a.id)

    def get_attempts(self, evaluation_id):
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

    def update_attempt(self, id, field, value):
        sql = 'UPDATE attempts SET {} = %s WHERE attempt_id = %s'.format(field)
        val = (value, id)
        try:
            self._execute_update_statement(sql, val)
        except Exception as e:
            self.logger.exception('[event=update-attempt-failure][attemptId=%s][updateField=%s][updateValue=%r]', id, field, value)
            raise ResourceAccessException(id, e)
        self.logger.info('[event=attempt-updated][attemptId=%s][updateField=%s][updateValue=%r]', id, field, value)

    def list_evaluations(self, owner_id):
        sql = 'SELECT * FROM evaluations WHERE owner_id = %s'
        val = (owner_id,)
        try:
            res = self._execute_select_many_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=get-evaluations-failure][ownerId=%s]', owner_id)
            raise ResourceAccessException(f'evaluations for {owner_id}', e)
        evaluations = []
        for row in res:
            evaluations.append(Evaluation.from_row(row))
        self.logger.info('[event=evaluations-retrieved][ownerId=%s][evaluationCount=%s]', owner_id, len(evaluations))
        return evaluations

    def check_is_owner(self, owner_id, evaluation_id):
        sql = 'SELECT owner_id FROM evaluations WHERE evaluation_id = %s'
        val = (evaluation_id,)
        res = self._execute_select_query(sql, val)
        if res is None:
            self.logger.error('[event=check-owner-failure][evaluationId=%s][userId=%s][message=no evaluation found]', evaluation_id, owner_id)
            raise ResourceNotFoundException(evaluation_id)
        if res[0] != owner_id:
            self.logger.error('[event=access-denied][evaluationId=%s][userId=%s]', evaluation_id, owner_id)
            raise PermissionDeniedException(evaluation_id, owner_id)
        else:
            self.logger.info('[event=owner-verified][evaluationId=%s][userId=%s]', evaluation_id, owner_id)

    def save_recording(self, attempt_id, recording):
        sql = 'INSERT INTO recordings (attempt_id, recording) VALUE (%s, %s)'
        val = (attempt_id, recording)
        try:
            self._execute_insert_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=save-recording-failure][attemptId=%s]', attempt_id)
            raise ResourceAccessException(attempt_id, e)
        self.logger.info('[event=recording-saved][attemptId=%s]', attempt_id)

    ''' General MySQL Interaction Methods '''

    def _execute_insert_query(self, sql, val):
        self.logger.info(self._make_info_log('db-insert', sql, (str(i) for i in val)))
        c = self.db.cursor()
        c.execute(sql, val)
        self.db.commit()

    def _execute_update_statement(self, sql, val):
        self.logger.info(self._make_info_log('db-update', sql, (str(i) for i in val)))
        c = self.db.cursor()
        c.execute(sql, val)
        self.db.commit()

    def _execute_select_query(self, sql, val):
        self.logger.info(self._make_info_log('db-select', sql, (str(i) for i in val)))
        c = self.db.cursor()
        c.execute(sql, val)
        return c.fetchone()

    def _execute_select_many_query(self, sql, val):
        self.logger.info(self._make_info_log('db-select-many', sql, (str(i) for i in val)))
        c = self.db.cursor()
        c.execute(sql, val)
        return c.fetchall()

    ''' Waiver Storage Methods '''

    def add_waiver(self, w):
        sql = ("INSERT INTO waivers ("
               "waiver_id, subject_name, subject_email, representative_name, relationship,"
               "date, signer, valid, filepath, owner_id) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %r, %s, %s);")
        val = (w.id, w.subject_name, w.subject_email, w.representative_name, w.relationship, w.date, w.signer, w.valid, w.filepath, w.owner_id)
        try:
            self._execute_insert_query(sql, val)
        except Exception as ex:
            self.logger.exception('[event=add-waiver-failure][subjectName=%s][subjectEmail=%s]', w.subject_name, w.subject_email)
            raise ResourceAccessException(None, ex)
        self.logger.info('[event=waiver-added][subjectName=%s][subjectEmail=%s]', w.subject_name, w.subject_email)

    def get_valid_waiver(self, user, subject_name, subject_email):
        sql = 'SELECT * FROM waivers WHERE subject_email = %s AND LOWER(subject_name) = LOWER(%s) AND valid = %r AND owner_id = %s;'
        val = (subject_email, subject_name.lower(), True, user)
        try:
            res = self._execute_select_query(sql, val)
        except Exception as e:
            self.logger.exception('[event=get-valid-waiver-failure][subjectEmail=%s]', subject_email)
            raise ResourceAccessException(None, e)

        w = None
        if res is not None:
            w = Waiver.from_row(res)
            self.logger.info('[event=valid-waiver-retrieved][subjectEmail=%s][waiverId=%s]', subject_email, w.id)
        else:
            self.logger.info('[event=no-valid-waiver-retrieved][subjectEmail=%s]', subject_email)
        return w

    def update_waiver(self, id, field, value):
        sql = 'UPDATE waivers SET {} = %s WHERE waiver_id = %s;'.format(field)
        val = (value, id)
        try:
            self._execute_update_statement(sql, val)
        except Exception as e:
            self.logger.exception('[event=update-waiver-failure][waiverId=%s][field=%s][value=%r]',
                                  id, field, value)
            raise ResourceAccessException(None, e)
        self.logger.info('[event=waiver-updated][waiverId=%s][field=%s][value=%r]',
                         id, field, value)

    def check_is_owner_waiver(self, user, waiver_id):
        sql = 'SELECT owner_id FROM waivers WHERE waiver_id = %s'
        val = (waiver_id,)
        res = self._execute_select_query(sql, val)
        if res[0] != user:
            self.logger.error('[event=access-denied][waiverId=%s][userId=%s]', waiver_id, user)
            raise PermissionDeniedException(waiver_id, user)
        else:
            self.logger.info('[event=owner-verified][waiverId=%s][userId=%s]', waiver_id, user)

    ''' Data Export Methods '''
    def export_data(self, start_date, end_date):
        sql = ("SELECT attempts.*, evaluations.age, evaluations.gender, evaluations.impression, recordings.recording"
               "FROM attempts "
               "INNER JOIN evaluations ON attempts.evaluation_id = evaluations.evaluation_id "
               "INNER JOIN recordings ON attempts.attempt_id = recordings.attempt_id "
               "WHERE attempts.date_created > %s and attempts.date_created < %s;"
               )
        val = (start_date, end_date)
        self.logger.info(self._make_info_log('super-query', 'large sql query', val))
        try:
            c = self.db.cursor()
            c.execute(sql, val)
            results = c.fetchall()
            self.logger.info('[event=super-query-complete][startDate=%s][endDate=%s][resultCount=%s]', start_date, end_date, len(results))
            return results
        except Exception as e:
            self.logger.exception('[event=super-query-failure][startDate=%s][endDate=%s]')
            raise ResourceAccessException(f'super query between {start_date} and {end_date}', e)

    def check_is_admin(self, user):
        sql = "SELECT * FROM admins WHERE id = %s"
        val = (user,)
        res = self._execute_select_query(sql, val)
        if res is None or res[0] != user:
            is_admin = False
        else:
            is_admin = True
        self.logger.info('[event=check-is-admin][user=%s][isAdmin=%s]', user, is_admin)
        return is_admin

    ''' Table Setup '''

    def _create_tables(self):
        create_evaluations_statement = ("CREATE TABLE IF NOT EXISTS `evaluations` ("
                                        "`evaluation_id` varchar(48) NOT NULL,"
                                        "`age` varchar(16) NOT NULL,"
                                        "`gender` varchar(16) NOT NULL,"
                                        "`impression` varchar(255) NOT NULL,"
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
                                     "`active` boolean NOT NULL DEFAULT TRUE,"
                                     "`syllable_count` integer NOT NULL,"
                                     "`date_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                                     "PRIMARY KEY (`attempt_id`),"
                                     "KEY `evaluation_id_idx` (`evaluation_id`),"
                                     "CONSTRAINT `evaluation_id` FOREIGN KEY (`evaluation_id`)"
                                     "REFERENCES `evaluations` (`evaluation_id`)"
                                     ");"
                                     )
        create_recordings_statement = ("CREATE TABLE IF NOT EXISTS `recordings` ("
                                       "`recording_id` int AUTO_INCREMENT NOT NULL,"
                                       "`attempt_id` varchar(48) NOT NULL,"
                                       "`date_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                                       "`recording` mediumblob NOT NULL,"
                                       "PRIMARY KEY (`recording_id`),"
                                       "KEY `attempt_id_idx` (`attempt_id`),"
                                       "CONSTRAINT `attempt_id` FOREIGN KEY (`attempt_id`)"
                                       "REFERENCES `attempts` (`attempt_id`)"
                                       ");"
                                       )
        create_waivers_statement = ("CREATE TABLE IF NOT EXISTS `waivers` ("
                                    "`waiver_id` varchar(48) NOT NULL,"
                                    "`subject_name` varchar(255) NOT NULL,"
                                    "`subject_email` varchar(255) NOT NULL,"
                                    "`representative_name` varchar(255),"
                                    "`relationship` varchar(255),"
                                    "`date` varchar(255) NOT NULL,"
                                    "`signer` varchar(48) NOT NULL,"
                                    "`valid` boolean NOT NULL DEFAULT TRUE,"
                                    "`filepath` varchar(255) NOT NULL,"
                                    "`owner_id` varchar(48) NOT NULL,"
                                    "PRIMARY KEY (`waiver_id`)"
                                    ");"
                                    )
        create_admins_statement = ("CREATE TABLE IF NOT EXISTS `admins` ("
                                   "`id` varchar(48) NOT NULL,"
                                   "PRIMARY KEY (`id`)"
                                   ");"
                                   )
        c = self.db.cursor()
        c.execute(create_evaluations_statement)
        c.execute(create_attempts_statement)
        c.execute(create_recordings_statement)
        c.execute(create_waivers_statement)
        c.execute(create_admins_statement)

    ''' RDS Setup '''

    @staticmethod
    def get_rds_password(host, user):
        import boto3
        access_key = os.environ['APX_AWS_ACCESS']
        secret_key = os.environ['APX_AWS_SECRET']
        region = os.environ.get('APX_AWS_REGION', 'us-west-2c')
        client = boto3.client('rds', region_name=region,
                              aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        token = client.generate_db_auth_token(DBHostname=host, Port=3306, DBUsername=user, Region=region)
        return token

    @staticmethod
    def _make_info_log(event, sql, val):
        fmt = '[event={event}][sql={sql}][vals={vals}]'

        str_vals = []
        for v in val:
            if isinstance(v, str) or isinstance(v, float) or isinstance(v, int):
                str_vals.append(v)
            else:
                str_vals.append('nonstring')

        if sql[0] == 'I':
            sql_msg = sql.split('VALUE', 0)[0]
        elif sql[0] in 'SU':
            sql_msg = sql
        else:
            sql_msg = 'unrecognized sql'
        return fmt.format(event=event, sql=sql_msg, vals='-'.join(str_vals))
