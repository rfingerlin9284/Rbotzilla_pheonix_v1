"use strict"

/** 
 * ChatClient
 * @description
 * Manages chat responses from the server.
 * 
 * @class
 * @property {string[]} messages
 * @property {string} userChatPrompt
 * */
export default class ChatClient {
	userChatPrompt: string;
	authIdToken: string;
	messages: {role: string, content: string}[];
	constructor() {
		this.userChatPrompt = "";
		this.authIdToken = "";
		this.messages = [];
	}

	/**
	 * @description
	 * Post a message to the chat server.
	 * @returns {Promise<Response>}
	 * @throws {Error}
	 * @throws {TypeError}
	 * @throws {SyntaxError}
	 * @throws {ReferenceError}
	 * @throws {RangeError}
	 * 
	 * @example
	 * const chatClient = new ChatClient();
	 * chatClient.userChatPrompt = "Hello World";
	 * chatClient.postChatMessage();
	 */
	async postChatMessage(): Promise<Response> {
		if (!this.userChatPrompt) throw new Error("Message is empty");
		if (this.userChatPrompt.length === 0) throw new Error("Message is empty");

		try {
			const body: string = JSON.stringify({ message: this.userChatPrompt });
			const response = await fetch("http://localhost:8000/chat", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"Authorization": `Bearer ${this.authIdToken}`
				},
				body: body,
			});
			return response;
		} catch (error) {
			console.error(error);
			throw error;
		}
	}
}
