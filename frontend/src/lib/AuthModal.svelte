<script lang="ts">
    import { authLoaded, authUser } from '$lib/auth'
    import { login, setAccountUsername, signup } from '$lib/api'
    import { sanitizeEmailInput, sanitizePasswordInput, sanitizeUsernameInput } from '$lib/input'
    import { PUBLIC_API_URL } from '$env/static/public'

    let {
        mode,
        usernameOnly = false,
        onClose,
    }: {
        mode: 'login' | 'signup'
        usernameOnly?: boolean
        onClose: () => void
    } = $props()

    let email = $state('')
    let password = $state('')
    let username = $state('')
    let errMsg = $state('')
    let saving = $state(false)
    let phase = $state<'credentials' | 'username'>('credentials')
    let activeMode = $state<'login' | 'signup'>('login')

    let isSignup = $derived(activeMode === 'signup')

    $effect(() => {
        activeMode = mode
        if (usernameOnly) phase = 'username'
    })

    function switchMode(nextMode: 'login' | 'signup') {
        activeMode = nextMode
        errMsg = ''
    }

    function continueWithGoogle() {
        window.location.href = `${PUBLIC_API_URL}/auth/google/start/`
    }

    async function handleCredentials() {
        const cleanEmail = sanitizeEmailInput(email)
        const cleanPassword = sanitizePasswordInput(password)
        email = cleanEmail
        password = cleanPassword
        errMsg = ''
        saving = true

        try {
            const user = isSignup
                ? await signup(cleanEmail, cleanPassword)
                : await login(cleanEmail, cleanPassword)
            authUser.set(user.authenticated ? user : null)
            authLoaded.set(true)
            if (user.needs_username) {
                phase = 'username'
                return
            }
            onClose()
        } catch (e) {
            errMsg = (e as Error).message
        } finally {
            saving = false
        }
    }

    async function handleUsername() {
        const cleanUsername = sanitizeUsernameInput(username)
        username = cleanUsername
        if (!cleanUsername) {
            errMsg = 'Username is required.'
            return
        }

        errMsg = ''
        saving = true

        try {
            const user = await setAccountUsername(cleanUsername)
            authUser.set(user)
            authLoaded.set(true)
            onClose()
        } catch (e) {
            errMsg = (e as Error).message
        } finally {
            saving = false
        }
    }

    function handleKey(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            if (phase === 'credentials') handleCredentials()
            else handleUsername()
        }
    }
</script>

<div class="overlay">
    <div class="modal">
        <button class="close-btn" onclick={onClose} aria-label="Close">x</button>

        {#if phase === 'credentials'}
            <p class="title">{isSignup ? 'Create Account' : 'Log In'}</p>
            <p class="subtitle">{isSignup ? 'Use an email and password to start your account.' : 'Enter your account email and password.'}</p>
            <input
                class="text-input"
                type="email"
                placeholder="Email"
                maxlength="254"
                bind:value={email}
                oninput={() => email = sanitizeEmailInput(email)}
                onkeydown={handleKey}
            />
            <input
                class="text-input"
                type="password"
                placeholder="Password"
                maxlength="128"
                bind:value={password}
                oninput={() => password = sanitizePasswordInput(password)}
                onkeydown={handleKey}
            />
            <button class="google-btn" onclick={continueWithGoogle}>
                <span>{isSignup ? 'Sign up' : 'Log in'} with Google</span>
                <span class="google-logo">G</span>
            </button>
            {#if isSignup}
                <p class="switch-text">
                    Already have an account?
                    <button class="switch-btn" onclick={() => switchMode('login')}>Log in here</button>
                </p>
            {:else}
                <p class="switch-text">
                    Don't have an account?
                    <button class="switch-btn" onclick={() => switchMode('signup')}>Sign up here</button>
                </p>
            {/if}
            {#if errMsg}
                <p class="error-text">{errMsg}</p>
            {/if}
            <div class="btn-row">
                <button class="dismiss-btn" onclick={onClose} disabled={saving}>Cancel</button>
                <button class="submit-btn" onclick={handleCredentials} disabled={saving}>
                    {saving ? 'Saving...' : isSignup ? 'Sign Up' : 'Log In'}
                </button>
            </div>
        {:else}
            <p class="title">{isSignup ? 'Account Created' : 'Choose Username'}</p>
            <p class="subtitle">Choose the username shown on your profile and leaderboard.</p>
            <input
                class="text-input"
                type="text"
                placeholder="Username"
                maxlength="30"
                bind:value={username}
                oninput={() => username = sanitizeUsernameInput(username)}
                onkeydown={handleKey}
            />
            {#if errMsg}
                <p class="error-text">{errMsg}</p>
            {/if}
            <div class="btn-row">
                <button class="submit-btn" onclick={handleUsername} disabled={saving}>
                    {saving ? 'Saving...' : 'Save Username'}
                </button>
            </div>
        {/if}
    </div>
</div>

<style>
.overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.modal {
    position: relative;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 2rem 2rem 1.5rem;
    max-width: 360px;
    width: 90%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    text-align: center;
}

.close-btn {
    position: absolute;
    top: 0.6rem;
    left: 0.75rem;
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 0.85rem;
    cursor: pointer;
    padding: 0.2rem 0.4rem;
    border-radius: var(--radius-sm);
    transition: color 0.15s;
}

.close-btn:hover { color: var(--text); }

.title {
    font-family: var(--font-display);
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
}

.subtitle {
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.03em;
}

.text-input {
    width: 100%;
    background: var(--surface-alt);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 0.5rem 0.75rem;
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 0.82rem;
    outline: none;
    transition: border-color 0.15s;
    text-align: center;
}

.text-input:focus { border-color: var(--gold); }

.google-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.55rem;
    background: var(--surface-alt);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-mid);
    font-family: var(--font-mono);
    font-size: 0.78rem;
    padding: 0.55rem 0.75rem;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s;
}

.google-btn:hover {
    border-color: var(--gold);
    color: var(--text);
}

.google-logo {
    width: 1.1rem;
    height: 1.1rem;
    border-radius: 50%;
    background: #fff;
    color: #4285f4;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
}

.switch-text {
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.03em;
}

.switch-btn {
    background: none;
    border: none;
    color: var(--gold);
    font: inherit;
    cursor: pointer;
    padding: 0;
}

.switch-btn:hover { text-decoration: underline; }

.error-text {
    font-size: 0.72rem;
    color: var(--error-text, #e05);
    letter-spacing: 0.03em;
}

.btn-row {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.25rem;
}

.dismiss-btn,
.submit-btn {
    padding: 0.5rem 1.25rem;
    border-radius: var(--radius-md);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.dismiss-btn {
    background: none;
    border: 1px solid var(--border);
    color: var(--text-dim);
}

.dismiss-btn:hover:not(:disabled) {
    border-color: var(--gold);
    color: var(--gold);
}

.submit-btn {
    background: var(--gold);
    border: 1px solid var(--gold);
    color: #0a0a0e;
    font-weight: 600;
}

.submit-btn:hover:not(:disabled) { filter: brightness(1.1); }

.dismiss-btn:disabled,
.submit-btn:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
