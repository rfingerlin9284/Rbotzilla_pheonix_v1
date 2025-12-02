<!-- /frontend/src/components/ChatWindow.svelte -->

<script lang="ts">
	import { onMount, afterUpdate } from "svelte";
	import MarkdownIt from "markdown-it";
	import AuctionAgent from "../lib/AuctionAgent"
	import { authentication } from "../stores/auth.store";

	let auctionAgent: AuctionAgent = new AuctionAgent();
	let chatWindowElement: HTMLDivElement;
	const markdownDecoder: MarkdownIt = new MarkdownIt();

	/**
	 * @function sendChatMessageAsync
	 * @description
	 * Send a message to the chat server and receive a response.
	 * @param {Event} event
	 * @returns void
	 */
	async function sendChatMessageAsync(event: Event) {
		try {
			if (!auctionAgent.auctionTitle) return;
			if (!auctionAgent.auctionDescription) return;

			auctionAgent.authIdToken = $authentication?.id_token ?? "";

			event.preventDefault();

			const response = await auctionAgent.postAuctionRequest();

			auctionAgent.messages = [...auctionAgent.messages,
					{ role: "user", content: auctionAgent.userChatPrompt }];
			auctionAgent.userChatPrompt = "";

			if (!ReadableStreamDefaultReader.prototype.hasOwnProperty(Symbol.asyncIterator)) {
				Object.defineProperty(ReadableStreamDefaultReader.prototype, Symbol.asyncIterator, {
					get() {
						return this;
					},
				});
			}
			const reader = response.body?.getReader();
			if (reader === null || reader === undefined) {
				throw new Error("Reader is null or undefined.");
			}

			const decoder = new TextDecoder("utf-8");
			let messageInMarkdownArray: string[] = [];

			let reading_data: boolean = true;
			while (reading_data) {
				
				const { done, value } = await reader.read();
				if (!done) {
					const chunk = decoder.decode(value, { stream: true });
					const partialChunkArray = chunk.split("\n");

					let partialChunk: string = "";
					let its_the_end = false;
					if (partialChunkArray.length >= 1) {
						for (const pc of partialChunkArray) {
							try {
								let dataPart: string = pc.trim();
								if (dataPart.length > 0) {
									const chatChunk = JSON.parse(pc);
									if (!chatChunk.is_end) {
										await displayBotMessageAsync(messageInMarkdownArray, chatChunk.content);
									} else {
										its_the_end = true;
									}
								}
							} catch (e) {
								console.error('Error processing partial chunk:', e, 'Partial chunk:', partialChunk);
							}
						}
					} else {
						if (partialChunkArray.length === 1) {
							partialChunk = partialChunkArray[0];
							partialChunk = partialChunk.trim();
							if (partialChunk.length > 0) {
								const chatChunk = JSON.parse(partialChunk);
								if (!chatChunk.is_end) {
									await displayBotMessageAsync(messageInMarkdownArray, chatChunk.content);
								} else {
									its_the_end = true;
								}
							}
						}
					}
					if (its_the_end) reading_data = false;
				} else {
					reading_data = false;
				}
			}
			messageInMarkdownArray.length = 0;
		} catch (error: unknown) {
			displayBotErrorAsync(error);
			console.error(error);
		}
	}

	function displayBotErrorAsync(error: unknown | Error | string) {
		let message: string = "Error: ";
		if (error instanceof Error) {
			message = message.concat(error.message);
		} else if (typeof error === "string") {
			message = message.concat(error);
		} else {
			message = "An error occurred.";
		}

		auctionAgent.messages = [...auctionAgent.messages, { role: "bot", content: message },];
	}

	function displayBotMessageAsync(chunks: string[], chunk: string) {
		if (chunk) {
			if (auctionAgent.messages[auctionAgent.messages.length - 1].role === "user") {
				chunks.push(chunk);
				auctionAgent.messages = [...auctionAgent.messages, { role: "bot", content: chunk },];
			} else {
				chunks.push(chunk);
				auctionAgent.messages[auctionAgent.messages.length - 1].content = markdownDecoder.render(chunks.join(""));
			}
		}
	}

	/**
	 * @function handleKeyDown
	 * @description
	 * Send a message to the chat server and receive a response.
	 * @param {KeyboardEvent} event
	 * @returns void
	 */
	async function handleKeyDown(event: KeyboardEvent) {
		// keyCode 13 is the Enter key
		const key = event.key || String.fromCharCode(event.keyCode);
		if ((key === 'Enter' || key === '\n') && !event.shiftKey) {
			await sendChatMessageAsync(event);
		}
	}

	/**
	 * @function handleClick
	 * @description
	 * Send a message to the chat server and receive a response.
	 * @param {MouseEvent} event
	 * @returns void
	 */
	 async function handleClick(event: MouseEvent) {
		try {
			if (event.shiftKey) {
				auctionAgent.userChatPrompt += "\n";
			} else {
				await sendChatMessageAsync(event);
			}
		} catch (error) {
			console.error(error);
		}
	}

	/**
	 * @function onMount
	 * @description
	 * Run after the component mounts.
	 * @param void
	 * @returns void
	 */
	 onMount(() => {
		try {
			chatWindowElement.focus();
			chatWindowElement.scrollTop = chatWindowElement.scrollHeight;
		} catch (error) {
			console.error(error);
		}
	});


	/**
	 * @function afterUpdate
	 * @description
	 * Run after the component updates.
	 * @param void
	 * @returns void
	 */
	 afterUpdate(() => {
		try {
			chatWindowElement.scrollTop = chatWindowElement.scrollHeight;
		} catch (error) {
			console.error(error);
		}
	});
</script>

<div class="chat-container">
	<!-- Input Section -->
	<div class="input-section">
		<input bind:value={auctionAgent.auctionTitle}
			   class="title-input"
			   placeholder="Enter auction title..."
			   maxlength="80"
		/>

		<textarea bind:value={auctionAgent.auctionDescription}
				  class="description-input"
				  placeholder="Paste auction description..."
				  rows={6}
		/>

		<button class="send-button" on:click={handleClick}>
		Generate Auction Details
		</button>
	</div>

	<!-- Output Section -->
	<div class="output-section">
		<div class="html-preview">
			<h3>Generated Listing HTML</h3>
			<div class="html-content">
				{@html auctionAgent.generatedHTML}
			</div>
		</div>

		<div class="auction-details">
			<h3>Auction Details</h3>
			<div class="details-grid">
				<div class="detail-item">
					<label for="final-title">Title:</label>
					<div id="final-title" class="detail-value">{auctionAgent.finalTitle}</div>
				</div>
				<!-- Add other detail items here -->
			</div>
		</div>
	</div>

	<!-- Chat History -->
	<div id="chat-window" bind:this={chatWindowElement} class="chat-history">
		{#each auctionAgent.messages as message, index (index)}
		<div class={`message ${message.role}`}>
			<p>{@html message.content}</p>
		</div>
		{/each}
	</div>
</div>

<style>
	/* Base styles */
	.chat-container {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		padding: 1rem;
		color: var(--text-color);
	}

	.input-section {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.title-input, .description-input {
		width: 100%;
		padding: 0.75rem;
		border-radius: 0.5rem;
		border: 1px solid var(--border-color);
		background-color: var(--input-bg);
		color: var(--text-color);
	}

	.description-input {
		min-height: 120px;
		resize: vertical;
	}

	.send-button {
		padding: 0.75rem 1.5rem;
		border-radius: 0.5rem;
		background-color: var(--primary-color);
		color: white;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.send-button:hover {
		background-color: var(--primary-hover);
	}

	.output-section {
		display: grid;
		gap: 1.5rem;
	}

	.html-preview, .auction-details {
		padding: 1.5rem;
		border-radius: 0.75rem;
		background-color: var(--surface-color);
	}

	.html-content {
		max-height: 300px;
		overflow-y: auto;
		background-color: var(--content-bg);
		padding: 1rem;
		border-radius: 0.5rem;
		margin-top: 1rem;
	}

	.details-grid {
		display: grid;
		gap: 1rem;
		margin-top: 1rem;
	}

  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .detail-value {
    padding: 0.75rem;
    border-radius: 0.5rem;
    background-color: var(--content-bg);
  }

  .chat-history {
    height: 400px;
    overflow-y: auto;
    padding: 1rem;
    border-radius: 0.75rem;
    background-color: var(--surface-color);
  }

  .message {
    max-width: 80%;
    padding: 0.75rem 1.25rem;
    margin-bottom: 0.75rem;
    border-radius: 0.75rem;
    word-wrap: break-word;
  }

  .message.user {
    background-color: var(--user-message-bg);
    color: white;
    margin-left: auto;
  }

  .message.bot {
    background-color: var(--bot-message-bg);
    margin-right: auto;
  }

  /* Light mode variables */
  :global(:root) {
    --text-color: #1a1a1a;
    --border-color: #e2e8f0;
    --input-bg: #ffffff;
    --primary-color: #3b82f6;
    --primary-hover: #2563eb;
    --surface-color: #f8fafc;
    --content-bg: #ffffff;
    --user-message-bg: #3b82f6;
    --bot-message-bg: #e2e8f0;
  }

	/* Dark mode variables */
	:global(.dark) {
		--text-color: #ffffff;
		--border-color: #4a5568;
		--input-bg: #2d3748;
		--primary-color: #2563eb;
		--primary-hover: #1e4bb5;
		--surface-color: #2d3748;
		--content-bg: #4a5568;
		--user-message-bg: #2563eb;
		--bot-message-bg: #4a5568;
	}
</style>