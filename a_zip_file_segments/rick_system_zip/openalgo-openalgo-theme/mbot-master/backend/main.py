#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: main.py

from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import json

from app.api.v1.endpoints import auction
from app.api.v1.endpoints import chat
from app.api.v1.endpoints import users
from mserv.mbot_config import MBotConfig, FastApiConnSettings
from mserv.mbot_delegate import MbotDelegate

appdelegate: MbotDelegate = MbotDelegate()
loaded: bool = appdelegate.load()

mbotconfig: MBotConfig = appdelegate.mbotconfig
fastapi_app: FastAPI = appdelegate.fastapi_app

conn_settings: FastApiConnSettings = mbotconfig.appconfig.connection_settings

fastapi_app.add_middleware(
	CORSMiddleware,
	allow_origins=conn_settings.allow_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

fastapi_app.include_router(chat.router)
fastapi_app.include_router(users.router)
fastapi_app.include_router(auction.router)

@fastapi_app.get("/")
def read_root() -> dict[str, str]:
	return {"app": mbotconfig.emojid}

@fastapi_app.get("/name")
def name() -> dict[str, str]:
	return {"name": mbotconfig.name}

@fastapi_app.get("/version")
def version() -> dict[str, str]:
	return {"version": mbotconfig.version}

@fastapi_app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}

@fastapi_app.get("/ping")
def ping() -> dict[str, str]:
	return {"ping": "pong"}
