<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import '../style.css'
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<nav>
	<a href="/">Home</a>
	<a href="/puzzle">Puzzle</a>
	<a href="/leaderboard">Leaderboard</a>
	<a href="/profile">Profile</a>
</nav>

{@render children()}

<style>
	nav {
		display: flex;
		gap: 1rem;
		padding: 1rem;
		background: #333;
	}

	a {
		color: white;
		text-decoration: none;
	}

	a:hover {
		text-decoration: underline;
	}
</style>
