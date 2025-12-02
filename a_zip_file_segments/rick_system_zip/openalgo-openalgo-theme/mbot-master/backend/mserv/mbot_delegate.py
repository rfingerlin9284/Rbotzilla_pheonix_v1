#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: mserv/mbot_delegate.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading
from mserv.mbot_config import MBotConfig, DynamoDbSettings, Sqlite3Settings

import aioboto3
import sqlite3
from typing import TypedDict

'''
CREATE TABLE IF NOT EXISTS user_data (
	oauth_vendor TEXT,
	user_id TEXT,
	email_address TEXT,
	login_info TEXT,
	PRIMARY KEY(oauth_vendor, user_id));
'''

class Sqite3Params(TypedDict):
	database: str

class Sqltie3Helper:

	_db_path: str
	_sqlite3_params: Sqite3Params
	_connection: sqlite3.Connection

	def __init__(self, db_settings: Sqlite3Settings):
		self._sqlite3_params = Sqite3Params()
		self._sqlite3_params.database = db_settings.database
		self._db_path = db_settings.database
	
	async def connect(self) -> sqlite3.Connection:
		if self._connection is None:
			self._connection = sqlite3.connect(self._db_path)
		return self._connection

	def close(self) -> None:
		if self._connection is not None:
			self._connection.close()
		return


class DynamoDBHelper:
	def __init__(self, db_settings: DynamoDbSettings):
		self._dynamodb_params = {
			"region_name": db_settings.region_name,
			"endpoint_url": db_settings.endpoint_url,
		}

	async def get_dynamodb(self):
		return await self.get_dynamodb_resource()

	async def get_dynamodb_resource(self):
		return await aioboto3.resource("dynamodb", **(self._dynamodb_params))

	async def get_dynamodb_client(self):
		return await aioboto3.client("dynamodb", **(self._dynamodb_params))

	async def exists(self, table_name) -> bool:
		result: bool = False
		return result

class MbotDelegate:
	_instance = None
	_lock = threading.Lock()  # Protects '_instance' during its first assignment
	_is_initialized: bool = False
	_is_loaded: bool = False
	fastapi_app: FastAPI
	mbotconfig: MBotConfig

	def __new__(cls, *args, **kwargs):
		with cls._lock:
			if not cls._instance:
				cls._instance = super(MbotDelegate, cls).__new__(cls)
				cls._is_initialized = False  # init is called after new
		return cls._instance

	def __init__(self):
		if self._is_initialized:
			return

		self._is_initialized = True # now initialized
		return

	def load(self) -> bool:
		if self._is_loaded:
			return True
		self._is_loaded = True
		lifespan = self.lifespan
		self.mbotconfig = MBotConfig.load("config.json")
		self.fastapi_app = FastAPI(lifespan=lifespan)
		return True

	async def load_async(self) -> bool:
		if self._is_loaded:
			return True
		self._is_loaded = True
		lifespan = self.lifespan
		self.mbotconfig = await MBotConfig.load_async("config.json")
		self.fastapi_app = FastAPI(lifespan=lifespan)
		return True

	@asynccontextmanager
	async def lifespan(self, app: FastAPI):
		db_settings: DynamoDbSettings = self.mbotconfig.appconfig.database_settings.dynamodb

		print("App Startup Events")

		yield
		print("App Shutdown Events")


	def db_settings(self) -> MBotConfig.ApplicationConfig.DatabaseSettings:
		return self.mbotconfig.appconfig.database_settings

	def is_initalized(self) -> bool:
		return self._is_initialized

	def unload(self) -> dict:
		self.fastapi_app = None
		return self.mbotconfig.unload()
