<script lang="ts">
    import favicon from '$lib/assets/favicon.svg';
    import '../style.css';
    import { page } from '$app/state';
    import { onMount } from 'svelte';
    import AuthModal from '$lib/AuthModal.svelte';
    import { authLoaded, authUser, logoutCurrentUser, refreshAuth } from '$lib/auth';

    let { children } = $props();
    let authModal = $state<{ mode: 'login' | 'signup'; usernameOnly?: boolean } | null>(null);
    let authError = $state('');

    const navLinks = [
        { href: '/',            label: 'Home' },
        { href: '/puzzles',     label: 'Puzzles' },
        { href: '/leaderboard', label: 'Leaderboard' },
        { href: '/tutorial',    label: 'Tutorial' },
        { href: '/about',       label: 'About' },
    ];

    onMount(() => {
        refreshAuth()
            .then((user) => {
                const params = new URLSearchParams(window.location.search);
                if (params.get('auth') === 'google' && user.authenticated && user.needs_username) {
                    authModal = { mode: 'signup', usernameOnly: true };
                }
                if (params.get('auth_error') === 'google') {
                    authError = 'Google sign in failed. Try again.';
                }
                if (params.has('auth') || params.has('auth_error')) {
                    window.history.replaceState({}, '', window.location.pathname);
                }
            })
            .catch(() => authLoaded.set(true));
    });

    async function handleLogout() {
        await logoutCurrentUser();
    }
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
        {#if $authUser?.username}
            <a href="/profile" class:active={page.url.pathname === '/profile'}>
                Profile
            </a>
        {/if}
    </div>
    <div class="nav-user">
        {#if !$authLoaded}
            <span class="guest">Loading</span>
        {:else if $authUser?.username}
            <span class="greeting">Welcome,</span>
            <span class="username">{$authUser.username}</span>
            <button class="auth-link" onclick={handleLogout}>Logout</button>
        {:else if $authUser}
            <span class="guest">Account</span>
            <button class="auth-link auth-primary" onclick={() => authModal = { mode: 'signup', usernameOnly: true }}>Set Username</button>
            <button class="auth-link" onclick={handleLogout}>Logout</button>
        {:else}
            <span class="guest">Guest</span>
            <button class="auth-link" onclick={() => authModal = { mode: 'login' }}>Login</button>
            <button class="auth-link auth-primary" onclick={() => authModal = { mode: 'signup' }}>Sign Up</button>
        {/if}
    </div>
</nav>

{#if authModal}
    <AuthModal
        mode={authModal.mode}
        usernameOnly={authModal.usernameOnly}
        onClose={() => authModal = null}
    />
{/if}

{#if authError}
    <div class="auth-error">
        <span>{authError}</span>
        <button onclick={() => authError = ''}>x</button>
    </div>
{/if}

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

.auth-link {
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.25rem 0.5rem;
    cursor: pointer;
}

.auth-link:hover {
    border-color: var(--gold);
    color: var(--gold);
}

.auth-primary {
    background: var(--gold);
    border-color: var(--gold);
    color: #0a0a0e;
}

.auth-primary:hover {
    color: #0a0a0e;
    filter: brightness(1.1);
}

.auth-error {
    position: fixed;
    right: 1rem;
    bottom: 1rem;
    z-index: 120;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: var(--error-bg);
    border: 1px solid var(--error-border);
    border-radius: var(--radius-md);
    color: var(--error-text);
    padding: 0.75rem 1rem;
    font-size: 0.76rem;
}

.auth-error button {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    font: inherit;
}
</style>
