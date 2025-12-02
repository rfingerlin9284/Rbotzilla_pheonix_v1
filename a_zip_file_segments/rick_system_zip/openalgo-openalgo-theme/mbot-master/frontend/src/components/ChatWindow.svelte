<!-- /frontend/src/components/ChatWindow.svelte -->

<script lang="ts">
	import { onMount, afterUpdate } from "svelte";
	import MarkdownIt from "markdown-it";
	import ChatClient from "../lib/ChatClient";
	import { authentication } from "../stores/auth.store";

	let chatClient: ChatClient = new ChatClient();
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
			if (!chatClient.userChatPrompt) return;

			chatClient.authIdToken = $authentication?.id_token ?? "";

			event.preventDefault();

			const response = await chatClient.postChatMessage();

			chatClient.messages = [...chatClient.messages,
					{ role: "user", content: chatClient.userChatPrompt }];
			chatClient.userChatPrompt = "";

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

		chatClient.messages = [...chatClient.messages, { role: "bot", content: message },];
	}

	function displayBotMessageAsync(chunks: string[], chunk: string) {
		if (chunk) {
			if (chatClient.messages[chatClient.messages.length - 1].role === "user") {
				chunks.push(chunk);
				chatClient.messages = [...chatClient.messages, { role: "bot", content: chunk },];
			} else {
				chunks.push(chunk);
				chatClient.messages[chatClient.messages.length - 1].content = markdownDecoder.render(chunks.join(""));
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
				chatClient.userChatPrompt += "\n";
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

<div id="chat-window" bind:this={chatWindowElement}
	 class="w-full h-96 overflow-auto p-4 bg-surface-200 rounded-lg variant-filled-surface">
	{#each chatClient.messages as message, index (index)}
		<div class="{message.role}
					{`message p-2 mb-2 rounded-lg ${message.role === 'user' ?
						'bg-blue-400 text-white ml-auto' :
						'bg-gray-400 text-black mr-auto'}`}">
			<p class="prose">{@html message.content}</p>
		</div>
	{/each}
</div>

<div id="mbot-prompt" class="mt-4 flex items-center">
	<textarea bind:value={chatClient.userChatPrompt}
			  on:keydown={handleKeyDown}
			  class="bg-surface-200 ring-0 flex-grow mx-2 p-2
						rounded-lg border-2 border-gray-200 text-black"
			  name="prompt"
			  id="prompt"
			  placeholder="Write a message..."
			  rows="1"
	/>
	<button class="variant-filled-primary bg-blue-500 text-white p-2
						rounded-lg"
			on:click={handleClick}>Send</button>
</div>

<style>
	.message {
		max-width: 80%;
		word-wrap: break-word;
	}
</style>
