import os
from threading import Lock

import mysql
import mysql.connector


class Database:
    def __init__(self):

        self._host_name_ = os.environ["DATABASE_HOST"]
        self._host_port_ = os.environ["DATABASE_PORT"]
        self._user_name_ = os.environ["DATABASE_USER"]
        self._user_password_ = os.environ["DATABASE_PASSWORD"]
        self._database_name_ = os.environ["DATABASE_DATABASE"]
        self._connection_ = None
        self._lock_ = Lock()
        self._create_connection_()

    def _create_connection_(self):
        """
        Establishes the connection between the database and the api_old
        :return:
        """
        self._connection_ = mysql.connector.connect(
            host=self._host_name_,
            port=self._host_port_,
            user=self._user_name_,
            passwd=self._user_password_,
            database=self._database_name_,
        )

        return self._connection_

    def execute(self, query, variables=None, commit=True):
        """
        Executes a query
        :param commit: If it should commit the changes
        :param query: The query to execute
        :param variables: The variables to prevent sql injection
        :return: The result of the query. Returns an empty list if there is no return value (for example in an 'insert into' query)
        """
        with self._lock_:
            if variables is None:
                variables = {}
            cursor = self._connection_.cursor()
            cursor.execute(query, variables)
            result = cursor.fetchall()
            cursor.close()
            if commit:
                self.commit()
            return result

    def commit(self):
        self._connection_.commit()

    def is_connected(self):
        return self._connection_ is not None

    def close(self, no_commit=False):
        """
        Commits the actions taken and closes the connection
        :return:
        """
        if not no_commit:
            self.commit()
        self._connection_.close()
