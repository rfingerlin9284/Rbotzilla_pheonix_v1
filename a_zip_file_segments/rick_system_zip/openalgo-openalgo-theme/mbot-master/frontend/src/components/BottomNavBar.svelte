<!-- /frontend/src/components/BottomNavBar.svelte -->
<script lang="ts">
	let terminalContent = `Here is the content of the terminal.
You can replace this with dynamic content.`;
</script>

<footer class="bottom-nav-bar">
	<pre>{terminalContent}</pre>
</footer>

<style>
	.bottom-nav-bar {
		position: fixed;
		bottom: 0;
		left: 0;
		width: 100%;
		height: 150px;
		padding: 1em;
		box-sizing: border-box;
		background: #1e1e1e;
		color: #fff;
		overflow-y: auto;
	}
</style>
