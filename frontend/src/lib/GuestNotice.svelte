<script lang="ts">
    let { message }: { message: string } = $props();
    let visible = $state(true);
</script>

{#if visible}
    <div class="overlay">
        <div class="modal">
            <button class="close-btn" onclick={() => visible = false} aria-label="Close">✕</button>
            <p class="title">You are not logged in</p>
            <p class="subtitle">{message}</p>
            <button class="dismiss-btn" onclick={() => visible = false}>Dismiss</button>
        </div>
    </div>
{/if}

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

.close-btn:hover {
    color: var(--text);
}

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

.dismiss-btn {
    margin-top: 0.5rem;
    padding: 0.5rem 1.5rem;
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s;
}

.dismiss-btn:hover {
    border-color: var(--gold);
    color: var(--gold);
}
</style>
