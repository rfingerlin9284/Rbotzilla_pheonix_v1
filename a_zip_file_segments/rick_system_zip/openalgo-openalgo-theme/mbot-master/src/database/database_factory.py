# -*- coding: utf-8 -*-

from .database import Database
from .database_sqlite3 import Sqlite3Database
from .database_mysql import MySqlDatabase
from .database_odbc import OdbcDatabase

from .database_type import DatabaseType
from .connection_information import ConnectionInfo

# Factory class
class DatabaseFactory:
	pass

	@classmethod
	def get_database_from_connection_info(cls, connection_info: ConnectionInfo) -> Database:
		match connection_info.db_type:
			case DatabaseType.MYSQL:
				return MySqlDatabase(connection_info)
			case DatabaseType.ODBC:
				return OdbcDatabase(connection_info)
			case DatabaseType.SQLITE:
				return Sqlite3Database(connection_info)
			case _:
				raise ValueError(f"Invalid database type: {connection_info.db_type}")
