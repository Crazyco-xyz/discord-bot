import mysql.connector
import mysql
import traceback
import os


class Database:
    def __init__(self):

        self._host_name_ = os.environ["DATABASE_HOST"]
        self._host_port_ = os.environ["DATABASE_PORT"]
        self._user_name_ = os.environ["DATABASE_USER"]
        self._user_password_ = os.environ["DATABASE_PASSWORD"]
        self._database_name_ = os.environ["DATABASE_DATABASE"]
        self._connection_ = None
        self.__create_connection__()

    def __create_connection__(self):
        """
        Establishes the connection between the database and the api_old
        :return:
        """
        try:
            self._connection_ = mysql.connector.connect(
                host=self._host_name_,
                port=self._host_port_,
                user=self._user_name_,
                passwd=self._user_password_,
                database=self._database_name_
            )
        except mysql.connector.errors.Error:
            print(f"An error has occurred while connecting to the database!")
            traceback.print_exc()

        return self._connection_

    def execute(self, query, variables=None, commit=False):
        """
        Executes a query
        :param commit: If it should commit the changes
        :param query: The query to execute
        :param variables: The variables to prevent sql injection
        :return: The result of the query. Returns an empty list if there is no return value (for example in an 'insert into' query)
        """

        if variables is None:
            variables = {}
        cursor = self._connection_.cursor()
        cursor.execute(query, variables)
        result = cursor.fetchall()
        if commit:
            cursor.commit()
        cursor.close()
        return result

    def commit(self):
        self._connection_.commit()

    def close(self):
        """
        Commits the actions taken and closes the connection
        :return:
        """
        self.commit()
        self._connection_.close()
