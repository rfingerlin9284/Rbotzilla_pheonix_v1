<!-- /frontend/src/routes/chat/+page.svelte -->
<script>
	import AuctionAgent from '../../components/AuctionAgent.svelte';
</script>

<svelte:head>
	<title>Auction Agent</title>
</svelte:head>

<div class="container p-10 space-y-4">
	<header class="bg-secondary p-4 flex justify-between items-center">
		<h2 class="h2 font-sans font-bold text-sm md:text-2xl tracking-widest">Auction Generator</h2>
	</header>
	<main>
		<div class="app-chat-block">
			<AuctionAgent />
		</div>
	</main>
</div>

<style>

</style>
