# -*- coding: utf-8 -*-

from .database import Database

# MySQL database
class MySqlDatabase(Database):
	def connect(self):
		import mysql.connector
		self.connection = mysql.connector.connect(
			user='username', password='password',
			host='hostname', database='dbname')

	def execute(self, query):
		cursor = self.connection.cursor()
		cursor.execute(query)

	def disconnect(self):
		self.connection.close()
