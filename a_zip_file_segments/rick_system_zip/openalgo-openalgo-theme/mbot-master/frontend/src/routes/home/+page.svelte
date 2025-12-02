<!-- /frontend/src/routes/home/+page.svelte -->
<script>
	import ChatWindow from '../../components/ChatWindow.svelte';
</script>

<svelte:head>
	<title>Home</title>
</svelte:head>

<div class="container p-10 space-y-4">
	<header class="bg-secondary p-4 flex justify-between items-center">
		<h2 class="h2 font-sans font-bold text-sm md:text-2xl tracking-widest">Home</h2>
	</header>
	<main>
		<div class="app-chat-block">
			Welcome
		</div>
	</main>
</div>

<style>

</style>
