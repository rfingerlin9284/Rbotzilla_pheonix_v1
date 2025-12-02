<!-- /frontend/src/routes/browser/+page.svelte -->
<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	type BrowserInfo = {
		appCodeName: string;
		appName: string;
		appVersion: string;
		clipboard: any;
		userAgent: string;
		connection: any;
		contacts: any;
		cookieEnabled: boolean;
		credentials: any;
		deviceMemory: any;
		doNotTrack: any;
		geolocation: any;
		globalPrivacyControl: any;
		onLine: boolean;
		gpu: any;
		pdfViewerEnabled: boolean;
		plugins: any;
		serviceWorker: any;
		storage: any;
		scheduling: any;
		language: string;
		onlineStatus: boolean;
		screenHeight: number;
		screenWidth: number;
		viewportHeight: number;
		viewportWidth: number;
	}

	function getPropertyFromString(obj: Object, str: string) : string | null {
		if (obj == null || str == null || str.length == 0) {
			throw new Error("Invalid arguments");
		}
		return obj.hasOwnProperty(str) ? (obj as any)[str] : null;
	}
	function getBrowserInfo() : BrowserInfo | null {
		var browserInfo : BrowserInfo | null = null;
		if (navigator == null) { return null; }
		try {
			browserInfo = {
				appCodeName: navigator.appCodeName,
				appName: navigator.appName,
				appVersion: navigator.appVersion,
				clipboard: navigator.clipboard,
				userAgent: navigator.userAgent,
				connection: getPropertyFromString(navigator, "connection"),
				contacts: getPropertyFromString(navigator, "contacts"),
				cookieEnabled: navigator.cookieEnabled,
				credentials: navigator.credentials,
				deviceMemory: getPropertyFromString(navigator, "deviceMemory"),
				doNotTrack: navigator.doNotTrack,
				geolocation: navigator.geolocation,
				globalPrivacyControl : getPropertyFromString(navigator, "globalPrivacyControl"),
				onLine: navigator.onLine,
				gpu: getPropertyFromString(navigator, "gpu"),
				pdfViewerEnabled: navigator.pdfViewerEnabled,
				plugins: navigator.plugins,
				serviceWorker: navigator.serviceWorker,
				storage: navigator.storage,
				scheduling: getPropertyFromString(navigator, "scheduling"),
				language: navigator.language,
				onlineStatus: navigator.onLine,
				screenHeight: window.screen.height,
				screenWidth: window.screen.width,
				viewportHeight: document.documentElement.clientHeight,
				viewportWidth: document.documentElement.clientWidth,
			};
	  } catch (e) {
		console.log(e);
	  }
	  return browserInfo;
	}
  
	let browserInfo : BrowserInfo | null = null;

	onMount(() => {
		browserInfo = getBrowserInfo();
		console.log("onMount");
	})
	onDestroy(() => {
		browserInfo = null;
		console.log("onDestroy");
	});

	// Executing the function and storing the information in a variable
</script>

<svelte:head>
	<title>Browser Information</title>
</svelte:head>

<div class="container p-10 space-y-4">
	<header class="bg-secondary p-4 flex justify-between items-center">
		<h2 class="h2 font-sans font-bold text-sm md:text-2xl tracking-widest">Browser Information</h2>
	</header>
	<main>
		<div class="w-full h-96 bg-center">
			<h1>Browser Information</h1>
			<ul>
				{#if (browserInfo != null)}
					{#each Object.entries(browserInfo) as [key, value]}
						<li><strong>{key}:</strong> {value}</li>
					{/each}
				{:else}
					<li>Browser information not available</li>
				{/if}
			</ul>
		</div>
	</main>
</div>

<style>
	div {
	  margin: 0 auto;
	  padding: 20px;
	  max-width: 600px;
	}
	ul {
	  list-style: none;
	  padding: 0;
	}
	li {
	  margin: 10px 0;
	}
</style>
