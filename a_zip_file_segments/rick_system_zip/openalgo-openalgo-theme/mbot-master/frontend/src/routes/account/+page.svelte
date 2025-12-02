<!-- /frontend/src/routes/about/+page.svelte -->
<script lang="ts">
	import type { User} from 'firebase/auth';
	import { onMount, onDestroy } from 'svelte';
	import { login, logout, authentication } from '../../stores/auth.store'
    import Login from '../../components/Login.svelte';
	
	let user: User | null = null;

	const unsubscribe = authentication.subscribe((value) => {
		user = value.user;
	});

	onDestroy(() => {
		user = null;
		unsubscribe();
	});

</script>

<svelte:head>
	<title>Account</title>
</svelte:head>

<div class="container p-10 space-y-4">
	<header class="bg-secondary p-4 flex justify-between items-center">
		<h2 class="h2 font-sans font-bold text-sm md:text-2xl tracking-widest">Account</h2>
	</header>
	<main>
		<div class="w-full h-96 bg-center">
			{#if user}
				<img src={user?.photoURL} alt={user?.displayName} class="h-12 w-12 avatar circle float-left" />
				<h3 class="h3">{user?.displayName}</h3>
				<p>{user?.email}</p>
				<p>Logged in with Google</p>
				<button on:click|stopPropagation={logout} class="logout-button">Logout</button>
			{:else}
				<div class="h-12">
					<p>You are not logged into the application.  Please login to continue.</p>
				</div>
				<div>
					<Login />
				</div>
			{/if}
		</div>
	</main>
</div>

<style>

</style>
