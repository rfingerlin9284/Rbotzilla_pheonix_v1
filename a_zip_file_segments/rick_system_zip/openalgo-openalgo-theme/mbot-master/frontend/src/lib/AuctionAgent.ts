"use strict"

/** 
 * AuctionAgent
 * @description
 * Manages chat responses from the server.
 * 
 * @class
 * @property {string[]} messages
 * @property {string} userChatPrompt
 * */
export default class AuctionAgent {
	userChatPrompt: string;
	authIdToken: string;
	auctionTitle: string;
	auctionDescription: string;
	generatedHTML: string;
	finalTitle: string;
	category: string;
	condition: string;
	price: string;
	shippingDetails: string;
	messages: {role: string, content: string}[];
	constructor() {
		this.userChatPrompt = "";
		this.authIdToken = "";
		this.auctionTitle = "";
		this.auctionDescription = "";
		this.generatedHTML = "";
		this.finalTitle = "";
		this.category = "";
		this.condition = "";
		this.price = "";
		this.shippingDetails = "";
		this.messages = [];
	}

		/**
	 * @description
	 * Post a message to the auction server.
	 * @returns {Promise<Response>}
	 * @throws {Error}
	 * @throws {TypeError}
	 * @throws {SyntaxError}
	 * @throws {ReferenceError}
	 * @throws {RangeError}
	 * 
	 * @example
	 * const auctionAgent = new AuctionAgent();
	 * auctionAgent.userChatPrompt = "Hello World";
	 * auctionAgent.postAuctionRequest();
	 */
		async postAuctionRequest(): Promise<Response> {

			if (!this.auctionTitle) throw new Error("Auction title is empty");
			if (this.auctionTitle.length === 0) throw new Error("Auction title is empty");

			if (!this.auctionDescription) throw new Error("Auction description is empty");
			if (this.auctionDescription.length === 0) throw new Error("Auction description is empty");

			try {
				const body: string = JSON.stringify({ suggested_title: this.auctionTitle, additional_information:this.auctionDescription });
				const response = await fetch("http://localhost:8000/auction", {
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
