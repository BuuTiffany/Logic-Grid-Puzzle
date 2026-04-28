<script lang="ts">
    import favicon from '$lib/assets/favicon.svg';
    import '../style.css';
    import { page } from '$app/state';

    let { children, data } = $props();

    const navLinks = [
        { href: '/',            label: 'Home' },
        { href: '/puzzle',      label: 'Puzzle' },
        { href: '/leaderboard', label: 'Leaderboard' },
        { href: '/profile',     label: 'Profile' },
    ];
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

<nav>
    <div class="nav-links">
        {#each navLinks as link}
            <a href={link.href} class:active={page.url.pathname === link.href}>
                {link.label}
            </a>
        {/each}
    </div>
    <div class="nav-user">
        {#if data.username}
            <span class="greeting">Welcome,</span>
            <span class="username">{data.username}</span>
        {:else}
            <span class="guest">Guest</span>
        {/if}
    </div>
</nav>

{@render children()}

<style>
nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 1.5rem;
    height: 52px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 50;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.nav-links a {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    text-decoration: none;
    padding: 0.4rem 0.75rem;
    border-radius: var(--radius-sm);
    transition: color 0.15s, background 0.15s;
}

.nav-links a:hover {
    color: var(--text);
    background: var(--surface-alt);
}

.nav-links a.active {
    color: var(--gold);
}

.nav-user {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-family: var(--font-mono);
    font-size: 0.72rem;
}

.greeting {
    color: var(--text-muted);
}

.username {
    color: var(--gold);
    letter-spacing: 0.05em;
}

.guest {
    color: var(--text-faint);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 0.65rem;
}
</style>
