# -*- coding: utf-8 -*-

from .database import Database

# SQLite database
class Sqlite3Database(Database):
	def connect(self):
		import sqlite3
		self.connection = sqlite3.connect('database.db')

	def execute(self, query):
		cursor = self.connection.cursor()
		cursor.execute(query)

	def disconnect(self):
		self.connection.close()
