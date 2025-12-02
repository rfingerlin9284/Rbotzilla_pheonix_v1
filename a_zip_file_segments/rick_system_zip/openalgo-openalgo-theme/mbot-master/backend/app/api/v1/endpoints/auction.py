# /backend/app/api/v1/endpoints/chat.py
# -*- coding: utf-8 -*-

import asyncio
import json
from fastapi import APIRouter, HTTPException, Request, status
from fastapi import Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator, Any, Optional, Tuple, Callable, TypeVar, Union, Generator
from uuid import UUID
from openai.types.chat import ChatCompletionChunk
from app.api.v1.utilites.firebase_token_verifier import FirebaseTokenVerifier
import os
import openai
from openai import AsyncStream
from typing import AsyncGenerator, Generator


OPENAI_PREVIEW: bool = True

# Load the function definition from a JSON file
with open("app/api/v1/function_auction_generator.json", "r") as f:
	create_auction_function = json.load(f)

# Load the OpenAI API key from the environment variables
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY_MBOT")
if OPENAI_API_KEY is None:
	raise Exception("OpenAI API key not found in environment variables")

# Load the Google Project ID from the environment variables
GOOGLE_PROJECT_ID: str | None = os.getenv("GOOGLE_PROJECT_ID_MBOT")
if GOOGLE_PROJECT_ID is None:
	raise Exception("Google Project ID not found in environment variables")

router: APIRouter = APIRouter()
if router is None:
	raise Exception("Failed to initialize API router")

async_openai_client: openai.AsyncOpenAI = openai.AsyncClient(api_key=OPENAI_API_KEY)
if async_openai_client is None:
	raise Exception("Failed to initialize OpenAI client")

chats: dict[UUID, list[dict[str, str]]] = {}

# Define the AuctionInput model
class AuctionInput(BaseModel):
	suggested_title: str
	additional_information: str

# Define the AuctionResponse model
class AuctionResponse(BaseModel):
	final_title: str
	category: str
	condition: str
	price: str
	shipping_details: str
	is_end: bool

# Get the current user ID from the request
async def get_current_user_id(request: Request) -> str:
	auth_token: str | None = request.headers.get('Authorization')
	if not auth_token:
		raise HTTPException(status_code=401, detail="Token is mis sing")

	auth_token = auth_token.replace("Bearer ", "")

	verifier: FirebaseTokenVerifier = FirebaseTokenVerifier(GOOGLE_PROJECT_ID)
	user_id: str = verifier.get_user_id(auth_token)

	if user_id is None:
		raise HTTPException(status_code=401, detail="User not authenticated")

	return user_id

async def get_auction_response_async(message: str) -> openai.AsyncStream[ChatCompletionChunk] | None:
	async_openai_client.chat.completions._get_api_list
	return await async_openai_client.chat.completions.create(
					model = "gpt-4o-mini",
					messages = [
						{"role": "system", "content": "You are a helpful assistant."},
						{"role": "user", "content": message},
						],
					stream = True
				)


@router.post("/auction", status_code=status.HTTP_200_OK)
async def auction_endpoint_async(
	auction_input: AuctionInput,
	user_id: str = Depends(get_current_user_id)
) -> StreamingResponse:
	# Validate input
	if not auction_input.suggested_title or not auction_input.additional_information:
		raise HTTPException(status_code=400, detail="Title and description are required")
	if len(auction_input.suggested_title) > 100:
		raise HTTPException(status_code=400, detail="Title too long")
	if len(auction_input.additional_information) > 1024:
		raise HTTPException(status_code=400, detail="Description too long")

	print("Auction Input:", auction_input)
	print("User ID:", user_id)

	async def event_stream_json_async() -> AsyncGenerator[str, None]:
		try:
			# Stream the OpenAI response with function calling
			stream = await async_openai_client.chat.completions.create(
				model="gpt-4",
				messages=[
					{"role": "system", "content": "You are an expert eBay auction creator. Generate professional auction details based on the provided title and description."},
					{"role": "user", "content": f"Title: {auction_input.suggested_title}\nDescription: {auction_input.additional_information}"},
				],
				tools=[create_auction_function],
				tool_choice={"type": "function", "function": {"name": "create_auction"}},
				stream=True
			)

			# Aggregate function call arguments
			tool_calls = {}
			async for chunk in stream:
				for tool_call in chunk.choices[0].delta.tool_calls or []:
					if tool_call.index not in tool_calls:
						tool_calls[tool_call.index] = {"arguments": "", "name": tool_call.function.name}

					if tool_call.function.arguments:
						tool_calls[tool_call.index]["arguments"] += tool_call.function.arguments

					# Yield partial results as they arrive
					if tool_calls[tool_call.index]["arguments"]:
						try:
							arguments = json.loads(tool_calls[tool_call.index]["arguments"])
							yield AuctionResponse(
								final_title=arguments.get("final_title", ""),
								category=arguments.get("category", ""),
								condition=arguments.get("condition", ""),
								price=arguments.get("price", ""),
								shipping_details=arguments.get("shipping_details", ""),
								is_end=False
							).model_dump_json() + "\n"
						except json.JSONDecodeError:
							# Skip incomplete JSON
							pass

			# Yield the final result
			for tool_call in tool_calls.values():
				arguments = json.loads(tool_call["arguments"])
				yield AuctionResponse(
					final_title=arguments.get("final_title", ""),
					category=arguments.get("category", ""),
					condition=arguments.get("condition", ""),
					price=arguments.get("price", ""),
					shipping_details=arguments.get("shipping_details", ""),
					is_end=True
				).model_dump_json() + "\n"

		except openai.RateLimitError as e:
			for error_response in await asyncio.to_thread(lambda: list(handle_openai_status_error(e, user_id))):
				yield error_response
		except openai.AuthenticationError as e:
			for error_response in await asyncio.to_thread(lambda: list(handle_openai_status_error(e, user_id))):
				yield error_response
		except openai.APIStatusError as e:
			for error_response in await asyncio.to_thread(lambda: list(handle_openai_status_error(e, user_id))):
				yield error_response
		except openai.APIError as e:
			raise HTTPException(status_code=500, detail=str(e.message))
		except Exception as e:
			raise HTTPException(status_code=400, detail=str(e))

	return StreamingResponse(event_stream_json_async(), media_type="application/x-ndjson")

def handle_openai_status_error(e: openai.APIStatusError, user_id: str) -> Generator[str, None, None]:
	error_array: list[str] = e.message.split(" ")
	max_index: int = len(error_array) - 1

	for i, chunk in enumerate(error_array):
		is_end: bool = (i == max_index)
		content: str = chunk + " " if chunk else ""
		yield AuctionResponse(user_id=user_id, content=content, is_end=is_end).model_dump_json() + "\n"
