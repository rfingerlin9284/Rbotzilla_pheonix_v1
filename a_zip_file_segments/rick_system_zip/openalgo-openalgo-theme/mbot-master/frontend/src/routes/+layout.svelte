<script lang="ts">
	//  These imports are required for the apps style to work...
	//  Order is important!  Do not change!  First is the theme, then the
	//     skeleton styles, then the app styles.
	// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	import '@skeletonlabs/skeleton/themes/theme-hamlindigo.css';
	import '@skeletonlabs/skeleton/styles/skeleton.css';
	import '../app.postcss';
	// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

	import {
		AppShell, AppBar, LightSwitch, Drawer, drawerStore
	} from '@skeletonlabs/skeleton';
	import Login from '../components/Login.svelte';
	import LeftNavBar from '../components/LeftNavBar.svelte';

	function drawerOpen(): void {
		drawerStore.open({});
	}

</script>

<Drawer><LeftNavBar /></Drawer>
<AppShell slotSidebarLeft="bg-surface-500/5 w-0 lg:w-64">
	<!-- Header Slot -->
	<svelte:fragment slot="header">
		<AppBar>
			<svelte:fragment slot="lead">
				<div class="flex items-center">
					<button class="lg:hidden btn btn-sm mr-4"
							on:click={drawerOpen}>
						<span>
							<svg viewBox="0 0 100 80"
								 class="fill-token w-4 h-4">
								<rect width="100" height="20" />
								<rect y="30" width="100" height="20" />
								<rect y="60" width="100" height="20" />
							</svg>
						</span>
					</button>
					<strong class="text-xl uppercase">mbot (💬🤖)</strong>
				</div>
			</svelte:fragment>
			<!--svelte:fragment slot="lead">
				💬🤖
			</svelte:fragment-->
			<svelte:fragment slot="trail">
				<LightSwitch /><div class="login-block"><Login /></div>
			</svelte:fragment>
			<!--svelte:fragment slot="headline">
				mbot
			</svelte:fragment-->
		</AppBar>
	</svelte:fragment>
	<!-- Left Sidebar Slot -->
	<svelte:fragment slot="sidebarLeft">
		<LeftNavBar />
	</svelte:fragment>
	<!-- Right Sidebar Slot -->
	<!-- Page Header Slot -->
	<!-- Router Slot -->
	<slot />
	<!-- Page Footer Slot -->
	<!-- App Footer Slot -->
</AppShell>

<style>
	.login-block {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 15px;
	}
</style>
