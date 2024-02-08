#!/usr/bin/env python3
"""filtered logs task.
"""
from typing import List
import os
import re
import logging
import mysql.connector


PII_FIELDS = ("email", "phone", "ssn", "password", "name")


def filter_datum(
        fields: List[str], redaction: str, message: str, separator: str,
        ) -> str:
    """ returns the log message obfuscated:
    """
    extrct = rf"({'|'.join(fields)})=([^{separator},]+)"
    mesage = re.sub(extrct, rf"\1={redaction}", message)
    return mesage


def get_logger() -> logging.Logger:
    """ function that takes no arguments
    and returns a logging.Logger object.
    """
    logger = logging.getLogger("user_data")
    stream_handler = logging.StreamHandler()
    logger.setLevel(logging.INFO)
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.propagate = False
    logger.addHandler(stream_handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """function that returns a connector to the database
    """
    database_host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    database_name = os.getenv("PERSONAL_DATA_DB_NAME", "")
    database_user = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    database_pwd = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    connection = mysql.connector.connect(
        host=database_host,
        port=3306,
        user=database_user,
        password=database_pwd,
        database=database_name,
    )
    return connection


def main():
    """retrieves the information about user.
    """
    database = get_db()
    cursor = database.cursor()
    cursor.execute("SELECT * FROM users;")
    logger = get_logger()
    for field in cursor:
        name, email, phone, ssn, password, ip, last_login, user_agent = field
        msg = f"name={name};email={email};"\
              f"phone={phone};ssn={ssn};ip={ip};"\
              f"password={password};last_login={last_login};"\
              f"user_agent={user_agent}"
        logger.info(msg)
    cursor.close()
    database.close()


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    FORMAT_FIELDS = ('name', 'levelname', 'asctime', 'message')
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """format arecord.
        """
        msg = super(RedactingFormatter, self).format(record)
        rec = filter_datum(self.fields, self.REDACTION, msg, self.SEPARATOR)
        return rec


if __name__ == "__main__":
    main()
