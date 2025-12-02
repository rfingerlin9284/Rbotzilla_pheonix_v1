<!-- /frontend/src/routes/+page.svelte -->
<script>
	import ChatWindow from '../components/ChatWindow.svelte';
</script>

<div class="container p-10 space-y-4">
	<header class="bg-secondary p-4 flex justify-between items-center">
		<h2 class="h2 font-sans font-bold text-sm md:text-2xl tracking-widest">Home</h2>
	</header>
	<main>
		<div class="app-chat-block">
			<ChatWindow />
		</div>
	</main>
</div>

<style>

</style>
