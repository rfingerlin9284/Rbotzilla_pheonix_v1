"use strict"

import MarkdownIt from "markdown-it";

/**
 * MessageBuilder
 * @description
 * This will take in a markdown message in chunks and transform it to HTML.
 * @class
 * @property {MarkdownIt} markdownDecoder
 * @property {string[]} tokens
 * @property {string[][]} blocks
 * 
 * @example
 * const messageBuilder = new MessageBuilder();
 * messageBuilder.addTokens("Hello", " ", "World", "\n\n", "How", " ", "are", " ", "you?");
 * messageBuilder.getBlockCount(); // 2
 *
 * // The first block is "Hello World"
 * messageBuilder.getBlockHtml(0); // "<p>Hello World</p>\n"
 *
 * // The second block is "How are you?"
 * messageBuilder.getBlockHtml(1); // "<p>How are you?</p>\n"
 */
export default class MessageBuilder {
	markdownDecoder: MarkdownIt;
	tokens: string[];
	blocks: string[][];
	/**
	 */
	constructor() {
		this.markdownDecoder = new MarkdownIt();
		this.tokens = [""];
		this.blocks = [[""]];
	}

	/**
	 * @description
	 * Add a token to the message.
	 * @param {string} token
	 * @throws {TypeError}
	 * @throws {Error}
	 */
	addToken(token: string) {
		if (typeof token !== "string") throw new TypeError("token must be a string");
		// if (token.length === 0) throw new Error("token is empty");
		this.tokens.push(token);
		if (this.tokens[this.tokens.length - 1] === "\n\n") {
			this.blocks.push([token]);
		} else {
			this.blocks[this.blocks.length - 1].push(token);
		}
	}

	/**
	 * @param {string[]} tokens
	 */
	addTokens(...tokens: string[]) {
		tokens.forEach(this.addToken);
	}

	/**
	 * @description
	 * Get the number of blocks.
	 * @returns {number}
	 * */
	getBlockCount(): number {
		return this.blocks.length;
	}

	/**
	 * Get the HTML for a block.
	 * @param {number} blockIndex
	 * @returns {string}
	 * @throws {TypeError}
	 * @throws {RangeError}
	 * @throws {Error}
	 * */
	getBlockHtml(blockIndex: number = this.blocks.length - 1): string {
		if (typeof blockIndex !== "number") throw new TypeError("blockIndex must be a number");
		if (blockIndex < 0) throw new RangeError("blockIndex must be greater than or equal to 0");
		if (blockIndex >= this.blocks.length) throw new RangeError("blockIndex must be less than the number of blocks");
		if (this.blocks[blockIndex].length === 0) throw new Error("blockIndex is empty");
		
		return this.markdownDecoder.render(this.blocks[blockIndex].join(""));
	}

	/**
	 * @description Message block decorator.
	 * @param {number} blockIndex
	 * @returns {string}
	 */
	decorateMessageBlock(blockIndex: number): string {
		let blockHtml = this.getBlockHtml(blockIndex);
		return `<p class="message-block">${blockHtml}</p>`;
	}
	
	/** 
	 * @description
	 * Get the HTML for the entire message.
	 * @returns {string}
	 * */
	getHtml(): string {
		let results = [""];
		for (let i = 0; i < this.blocks.length; i++) {
			results.push(this.decorateMessageBlock(i));
		}
		return results.join("");
	}
}
