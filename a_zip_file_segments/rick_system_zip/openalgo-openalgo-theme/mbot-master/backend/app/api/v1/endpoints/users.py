#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mserv.mbot_config import MBotConfig
from mserv.mbot_delegate import MbotDelegate

from fastapi import APIRouter, FastAPI, HTTPException, Path
from boto3.dynamodb.conditions import Key
import aioboto3
import os

mbotdelgate: MbotDelegate = MbotDelegate()
router: APIRouter = APIRouter()			# Initalize the FastAPI router

# Get the service resource.
async def get_dynamodb():
	db_settings: MBotConfig.ApplicationConfig.DatabaseSettings = mbotdelgate.db_settings()
	dynamodb_params = {
		"region_name": "us-east-1",
		"endpoint_url": db_settings.dynamodb.endpoint_url,
	}
	return aioboto3.resource("dynamodb", **dynamodb_params)

#@app.on_event("startup")
#async def startup_event():
#	dynamodb = await get_dynamodb()
