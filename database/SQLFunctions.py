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
        self.host = "localhost"
        self.logger = logging.getLogger('rotom')
        with open("config.json") as c:
            config = json.load(c)
            self.username = config['database']['user']
            self.password = config['database']['password']
            self.database = config['database']['database']

    def add_warn(self, user: int, author: int, name: str, reason: str):
        values = (user, author, name, reason, datetime.now())
        try:
            with mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    database=self.database
            ) as db:
                with db.cursor() as cursor:
                    cursor.execute(add_warn, values)
                    db.commit()
        except Exception as e:
            self.logger.exception(e)
            raise

    def count_warns(self, user: int):
        func = count_warns.format(user)
        try:
            with mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    database=self.database
            ) as db:
                with db.cursor() as cursor:
                    cursor.execute(func)
                    count = cursor.fetchone()[0]
                    return count
        except Exception as e:
            self.logger.exception(e)
            raise

    def get_all_ids(self):
        try:
            with mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    database=self.database
            ) as db:
                with db.cursor() as cursor:
                    cursor.execute(get_warn_id)
                    return cursor.fetchall()
        except Exception as e:
            self.logger.exception(e)
            raise

    def get_all_warns(self, user):
        func = get_all_warns.format(user)
        try:
            with mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    database=self.database
            ) as db:
                with db.cursor() as cursor:
                    cursor.execute(func)
                    return cursor.fetchall()
        except Exception as e:
            self.logger.exception(e)
            raise

    def get_all_warn_id(self, user_id: int):
        func = get_all_warn_id.format(user_id)
        try:
            with mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    database=self.database
            ) as db:
                with db.cursor() as cursor:
                    cursor.execute(func)
                    return cursor.fetchall()
        except Exception as e:
            self.logger.exception(e)
            raise

    def remove_warn(self, warn_id: int):
        func = delete_warn.format(warn_id)
        try:
            with mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    database=self.database
            ) as db:
                with db.cursor() as cursor:
                    cursor.execute(func)
                    db.commit()
        except Exception as e:
            self.logger.exception(e)
            raise

    def check_warn_exist(self, warn_id):
        func = check_warn_exist.format(warn_id)
        try:
            with mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    database=self.database
            ) as db:
                with db.cursor() as cursor:
                    cursor.execute(func)
                    return cursor.fetchone()
        except Exception as e:
            self.logger.exception(e)
            raise
