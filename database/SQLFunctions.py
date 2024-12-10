import json
import mysql.connector
import logging

from datetime import datetime

add_warn = "INSERT INTO warns (user_id, author_id, author_name, reason, date_time) VALUES (%s, %s, %s, %s, %s)"
count_warns = "SELECT COUNT(*) FROM warns WHERE user_id = {}"
check_warn_exist = "SELECT 1 FROM warns WHERE warn_id = {}"
get_warn_id = "SELECT warn_id FROM warns"
get_all_warns = "SELECT * FROM warns WHERE user_id = {}"
get_all_warn_id = "SELECT warn_id FROM warns WHERE user_id = {}"
delete_warn = "DELETE FROM warns WHERE warn_id = {}"


class Database:
    def __init__(self):
        self.logger = logging.getLogger('rotom')
        with open("config.json") as c:
            config = json.load(c)
            self.host = config['database']['host']
            self.username = config['database']['user']
            self.password = config['database']['password']
            self.database = config['database']['database']

        try:
            self.cnx = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database
            )

            self.cursor = self.cnx.cursor()
        except Exception as e:
            self.logger.error(e)
            raise e

    def add_warn(self, user: int, author: int, name: str, reason: str):
        values = (user, author, name, reason, datetime.now())
        try:
            self.cursor.execute(add_warn, values)
            self.cnx.commit()
        except Exception as e:
            self.logger.exception(e)
            raise

    def count_warns(self, user: int):
        func = count_warns.format(user)
        try:
            self.cursor.execute(func)
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.logger.exception(e)
            raise

    def get_all_ids(self):
        try:
            self.cursor.execute(get_warn_id)
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.exception(e)
            raise

    def get_all_warns(self, user):
        func = get_all_warns.format(user)
        try:
            self.cursor.execute(func)
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.exception(e)
            raise

    def get_all_warn_id(self, user_id: int):
        func = get_all_warn_id.format(user_id)
        try:
            self.cursor.execute(func)
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.exception(e)
            raise

    def remove_warn(self, warn_id: int):
        func = delete_warn.format(warn_id)
        try:
            self.cursor.execute(func)
            self.cnx.commit()
        except Exception as e:
            self.logger.exception(e)
            raise

    def check_warn_exist(self, warn_id):
        func = check_warn_exist.format(warn_id)
        try:
            self.cursor.execute(func)
            return self.cursor.fetchone()
        except Exception as e:
            self.logger.exception(e)
            raise
