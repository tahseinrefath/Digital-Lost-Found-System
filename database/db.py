import mysql.connector

from flask import g

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE
)


# ============================================================
# MYSQL DATABASE CONNECTION
# ============================================================

class DatabaseConnection:
    """
    Small wrapper around the MySQL connection.

    This allows the rest of the Flask application to continue
    using:

        db.execute(...)
        db.commit()

    just like the previous SQLite version.
    """

    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=None):
        """
        Execute a SQL query and return a dictionary cursor.
        """

        cursor = self.connection.cursor(
            dictionary=True
        )

        # MySQL uses %s instead of SQLite's ?
        query = query.replace("?", "%s")

        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(
                query,
                params
            )

        return cursor

    def commit(self):
        """
        Save database changes.
        """

        self.connection.commit()

    def close(self):
        """
        Close the MySQL connection.
        """

        self.connection.close()


# ============================================================
# GET DATABASE
# ============================================================

def get_db():
    """
    Get the MySQL database connection for the current request.
    """

    if "db" not in g:

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        g.db = DatabaseConnection(
            connection
        )

    return g.db


# ============================================================
# CLOSE DATABASE
# ============================================================

def close_db(error=None):
    """
    Close the MySQL connection when the Flask request ends.
    """

    db = g.pop(
        "db",
        None
    )

    if db is not None:
        db.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    """
    Check that the MySQL database can be reached.

    The database and tables are created using schema.sql
    through MySQL Workbench.
    """

    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )

    cursor = connection.cursor()

    cursor.execute(
        f"USE `{MYSQL_DATABASE}`"
    )

    cursor.close()
    connection.close()