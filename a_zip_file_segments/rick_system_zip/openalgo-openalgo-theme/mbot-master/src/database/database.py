# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

class Database(ABC):
	@abstractmethod
	def connect(self, **kwargs):
		pass

	@abstractmethod
	def execute(self, query):
		pass

	@abstractmethod
	def disconnect(self):
		pass
