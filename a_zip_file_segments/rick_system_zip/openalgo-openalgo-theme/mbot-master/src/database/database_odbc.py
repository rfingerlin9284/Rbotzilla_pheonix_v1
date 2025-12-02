# -*- coding: utf-8 -*-

from .database import Database

# ODBC database
class OdbcDatabase(Database):
	def connect(self):
		import pyodbc
		f = pyodbc(autocommit=True)
		f.connect()
		self.connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=hostname;DATABASE=dbname;UID=username;PWD=password')

	def execute(self, query):
		cursor = self.connection.cursor()
		cursor.execute(query)

	def disconnect(self):
		self.connection.close()
