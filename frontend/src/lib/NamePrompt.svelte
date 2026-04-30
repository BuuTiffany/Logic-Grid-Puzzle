<script lang="ts">
    import { submitSolve } from '$lib/api';
    import { sanitizeUsernameInput } from '$lib/input';

    let {
        puzzle_id,
        grid,
        difficulty,
        solve_time,
        onClose,
    }: {
        puzzle_id: string;
        grid: string;
        difficulty: string;
        solve_time: number;
        onClose: () => void;
    } = $props();

    let username = $state('');
    let saving   = $state(false);
    let saved    = $state(false);
    let errMsg   = $state('');

    async function handleSubmit() {
        const trimmed = sanitizeUsernameInput(username);
        username = trimmed;
        if (!trimmed) { onClose(); return; }
        saving = true;
        errMsg = '';
        try {
            await submitSolve({ username: trimmed, puzzle_id, grid, difficulty, solve_time });
            saved = true;
            setTimeout(onClose, 1500);
        } catch (e) {
            errMsg = (e as Error).message;
        } finally {
            saving = false;
        }
    }

    function handleKey(e: KeyboardEvent) {
        if (e.key === 'Enter') handleSubmit();
    }
</script>

<div class="overlay">
    <div class="modal">
        {#if saved}
            <p class="title">Saved!</p>
            <p class="subtitle">Your solve has been recorded.</p>
        {:else}
            <button class="close-btn" onclick={onClose} aria-label="Close">✕</button>
            <p class="title">Puzzle Solved!</p>
            <p class="subtitle">Enter your name to save your time to the leaderboard.</p>
            <input
                class="name-input"
                type="text"
                placeholder="Your name"
                maxlength="30"
                bind:value={username}
                oninput={() => username = sanitizeUsernameInput(username)}
                onkeydown={handleKey}
            />
            {#if errMsg}
                <p class="error-text">{errMsg}</p>
            {/if}
            <div class="btn-row">
                <button class="dismiss-btn" onclick={onClose} disabled={saving}>Skip</button>
                <button class="submit-btn"  onclick={handleSubmit} disabled={saving}>
                    {saving ? 'Saving…' : 'Submit'}
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

.name-input {
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

.name-input:focus { border-color: var(--gold); }

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
.submit-btn:disabled  { opacity: 0.4; cursor: not-allowed; }
</style>
