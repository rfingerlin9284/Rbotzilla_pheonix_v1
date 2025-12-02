# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from .database_type import DatabaseType

class ConnectionInfo(ABC):
	@abstractmethod
	def __init__(self, db_type: DatabaseType, host: str, port: int, username: str, password: str, database: str):
		self.db_type = db_type
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.database = database

class OdbcConnectionInfo(ConnectionInfo):
	def __init__(self, host: str, port: int, username: str, password: str, database: str):
		super().__init__(DatabaseType.ODBC, host, port, username, password, database)

class SQLiteConnectionInfo(ConnectionInfo):
	def __init__(self, database: str):
		super().__init__(DatabaseType.SQLITE, None, None, None, None, database)

class MySQLConnectionInfo(ConnectionInfo):
	def __init__(self, host: str, port: int, username: str, password: str, database: str):
		super().__init__(DatabaseType.MYSQL, host, port, username, password, database)

# from .database_factory import DatabaseFactory
# 
# connectionInfo = SQLiteConnectionInfo("/User/michael/Projects/tmp/test_db.db")
# sqlite_database = DatabaseFactory.get_database_from_connection_info(connectionInfo)
# sqlite_database.connect()
# sqlite_database.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, password TEXT NOT NULL)")
# sqlite_database.execute("INSERT INTO users (name, email, password) VALUES ('John Doe', 'johnd@example.com', 'password123')")
# sqlite_database.disconnect()
