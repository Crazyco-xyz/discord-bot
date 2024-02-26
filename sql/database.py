import sqlite3


class Database:
    def __init__(self, database_path: str):
        self._db_path_ = database_path
        self._db_ = None

    def open(self):
        self._db_ = sqlite3.connect(self._db_path_)

    def execute(self, query, variables=None):
        """
        Executes a query
        :param query: The query to execute
        :param variables: The variables to prevent sql injection
        :return: The result of the query. Returns an empty list if there is no return value (for example in an 'insert into' query)
        """

        if variables is None:
            variables = {}
        cursor = self._db_.cursor()
        cursor.execute(query, variables)
        result = cursor.fetchall()
        cursor.close()
        return result
