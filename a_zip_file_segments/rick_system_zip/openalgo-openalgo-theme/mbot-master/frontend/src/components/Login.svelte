<!-- /frontend/src/components/Login.svelte -->
<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { login, logout, authentication } from '../stores/auth.store'
	import type { User} from 'firebase/auth';

	let user: User | null = null;
	let showTooltip: boolean = false;

	const unsubscribe = authentication.subscribe((value) => {
		user = value.user;
	});

	onDestroy(() => {
		user = null;
		unsubscribe();
	});

	function openTooltip() {
		showTooltip = true;
	}

	function closeTooltip() {
		showTooltip = false;
	}

	function onClickInside(e: MouseEvent & { currentTarget: EventTarget & HTMLDivElement; }) {
		showTooltip = !showTooltip;
		//e.stopPropagation();
	}

	function onKeydown(e: KeyboardEvent & { currentTarget: EventTarget & HTMLDivElement; }) {
		if (e.key === 'Enter' || e.key === 'Space') {
			openTooltip();
			e.preventDefault();
		}
		console.log(e);
	}

</script>

{#if user}
	<div class="items-center space-x-2 xl:inline-flex">
		<div class="avatar-container"
			 on:click={onClickInside}
			 on:blur={closeTooltip}
			 on:keydown={onKeydown}
			 role="button" tabindex="0">
			<img src={user?.photoURL}
				 alt={user?.displayName}
				 class="h-12 w-12 avatar circle" />
	{#if showTooltip} 
			<div class="avatar-tooltip" style="display: block;">
				<p>{user?.displayName}</p>
				<p>{user?.email}</p>
				<p>Logged in with Google</p>
				<button on:click|stopPropagation={logout} class="logout-button">Logout</button>
			</div>
	{/if}
		</div>
	</div>
{:else}
	<button on:click={login} class="login-button">Login</button>
{/if}

<style>
	/*General Styles*/
	/*
	.login-block {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 15px;
	}
	*/
	/*
	.placeholder {
		flex-grow: 1;
	}
	*/
	.avatar-container {
		position: relative;
		cursor: pointer;
	}
	
	/*Avatar Styles*/
	.avatar.circle {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		object-fit: cover;
	}
	
	/*Tooltip Styles*/
	.avatar-tooltip {
		display: none;
		position: absolute;
		background-color: #333;
		color: #fff;
		padding: 15px;
		border-radius: 10px;
		top: 100%;
		right: 0;
		transform: translateY(10px);
		width: 200px;
		z-index: 1;
		box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
	}
	
	.avatar-tooltip p {
		margin-bottom: 10px;
	}
	
	.avatar-tooltip::after {
		content: '';
		position: absolute;
		top: 0;
		right: 15px;
		border-width: 5px;
		border-style: solid;
		border-color: #333 transparent transparent transparent;
	}
	
	/*
	.avatar-container:hover .avatar-tooltip, 
	.avatar-container:active .avatar-tooltip {
		display: block;
	}
	*/
	
	/*Button Styles*/
	.logout-button, .login-button {
		padding: 10px 20px;
		border: none;
		border-radius: 4px;
		color: #fff;
		cursor: pointer;
		transition: all 0.3s ease;
	}
	
	.logout-button {
		background-color: #f44336; 
	}
	
	.logout-button:hover {
		background-color: #d32f2f;
	}
	
	.login-button {
		background-color: #4285F4; 
	}
	
	.login-button:hover {
		background-color: #3367d6;
	}
	
	@media screen and (max-width: 768px) {
		.items-center {
			flex-direction: column;
		}
	}
</style>
