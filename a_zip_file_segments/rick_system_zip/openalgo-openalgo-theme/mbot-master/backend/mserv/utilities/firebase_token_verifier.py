#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: mserv/utilities/mfirebase_token_verifier.py

from jose import jwt, JWTError, JOSEError
import requests
from typing import Optional
from fastapi import HTTPException

class FirebaseTokenVerifier:
	GOOGLE_CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
	GOOGLE_ISSUER = "https://securetoken.google.com/[YOUR_PROJECT_ID]"

	def __init__(self, project_id: str):
		self.project_id = project_id
		self.GOOGLE_ISSUER = self.GOOGLE_ISSUER.replace("[YOUR_PROJECT_ID]", project_id)

	def _fetch_google_certs(self) -> dict:
		response = requests.get(self.GOOGLE_CERTS_URL)
		if response.status_code == 200:
			return response.json()
		else:
			response.raise_for_status()

	#def _fetch_google_certs(self) -> dict:
	#	return requests.get(self.GOOGLE_CERTS_URL).json()

	def decode_token(self, token: str) -> dict:
		certs: dict = self._fetch_google_certs()
		
		# Extract the Key ID from the JWT header without verification
		unverified_header = jwt.get_unverified_header(token)
		kid: str = unverified_header['kid']
		auth_algorithm: str = unverified_header['alg']
		key: str | None = None

		# Find the key we need based on the Key ID
		if kid in certs:
			key = certs[kid]
		else:
			raise ValueError('Key ID from token not found in Google certs.')

		try:
			return jwt.decode(
				token=token,
				key=key,
				algorithms=[auth_algorithm],
				audience=self.project_id,
				issuer=self.GOOGLE_ISSUER
			)
		except JWTError as e:
			raise HTTPException(status_code=401, detail=str(e))
		except JOSEError as e:
			raise HTTPException(status_code=401, detail=str(e))
		except Exception as e:
			raise HTTPException(status_code=500, detail="Internal server error")
	
	def get_user_id(self, token: str) -> Optional[str]:
		decoded_token = self.decode_token(token)
		return decoded_token.get("user_id", None)
