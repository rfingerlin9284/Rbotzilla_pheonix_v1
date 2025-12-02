<!-- /frontend/src/components/LeftNavBar.svelte -->
<script lang="ts">
	import { drawerStore } from '@skeletonlabs/skeleton';

	let items: {title: string; content: string; anchor: string; }[] = [
		{ title: 'Home', content: 'Home', anchor: '/' },
		{ title: 'Auction Agent', content: 'AuctionAgent', anchor: '/auction' },
		{ title: 'Chat', content: 'Chat', anchor: '/chat' },
		{ title: 'Account', content: 'Account', anchor: '/account' },
		{ title: 'Browser', content: 'Browser', anchor: '/browser' },
		{ title: 'About', content: 'About', anchor: '/about' },
	];

	function drawerClose(): void {
		drawerStore.close();
	}

</script>

<nav class="list-nav p-4">
	<ul>
		{#each items as item (item.title)}
			<li>
				<a href="{item.anchor}" title="{item.title}"
				   on:click={drawerClose}>
					{item.content}
				</a>
			</li>
		{/each}
	</ul>
</nav>

<style>

</style>
