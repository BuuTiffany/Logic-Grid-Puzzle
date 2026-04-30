<script lang="ts">
    import { goto } from '$app/navigation'

    const GRIDS = ['3x4', '3x5', '4x4', '4x5', '4x6', '4x7']
    const DIFFICULTIES = ['easy', 'moderate', 'challenging']

    const GRID_LABELS: Record<string, string> = {
        '3x4': '3 categories · 4 houses',
        '3x5': '3 categories · 5 houses',
        '4x4': '4 categories · 4 houses',
        '4x5': '4 categories · 5 houses',
        '4x6': '4 categories · 6 houses',
        '4x7': '4 categories · 7 houses',
    }

    const DIFF_LABELS: Record<string, string> = {
        easy:        'More clues, gentler logic chains.',
        moderate:    'Balanced challenge for most solvers.',
        challenging: 'Minimal clues. No hand-holding.',
    }

    let selectedGrid = '4x5'
    let selectedDifficulty = 'moderate'

    function startPuzzle() {
        goto(`/puzzle?grid=${selectedGrid}&difficulty=${selectedDifficulty}`)
    }
</script>

<div class="bg-grid"></div>

<main class="landing">
    <header class="landing-header">
        <div class="logo-mark">◈</div>
        <h1>Choose Puzzle</h1>
        <p class="label-dim tagline">Pick a grid. Set the difficulty. Start solving.</p>
    </header>

    <div class="card landing-card">
        <section class="option-section">
            <div class="section-header">
                <span class="label-sm">01</span>
                <h2>Grid Size</h2>
            </div>
            <div class="grid-options">
                {#each GRIDS as grid}
                    <button
                        class="grid-btn"
                        class:active={selectedGrid === grid}
                        on:click={() => selectedGrid = grid}
                    >
                        <span class="grid-code">{grid}</span>
                        <span class="grid-sub">{GRID_LABELS[grid]}</span>
                    </button>
                {/each}
            </div>
        </section>

        <div class="divider"></div>

        <section class="option-section">
            <div class="section-header">
                <span class="label-sm">02</span>
                <h2>Difficulty</h2>
            </div>
            <div class="diff-options">
                {#each DIFFICULTIES as diff}
                    <button
                        class="diff-btn"
                        class:active={selectedDifficulty === diff}
                        on:click={() => selectedDifficulty = diff}
                    >
                        <span class="diff-name">{diff}</span>
                        <span class="diff-desc">{DIFF_LABELS[diff]}</span>
                    </button>
                {/each}
            </div>
        </section>

        <button class="btn-primary start-btn" on:click={startPuzzle}>
            <span>Begin Puzzle</span>
            <span class="arrow">→</span>
        </button>
    </div>

    <footer class="landing-footer">
        <span class="label-dim">{selectedGrid} · {selectedDifficulty}</span>
    </footer>
</main>

<style>
    .landing {
        position: relative;
        z-index: 1;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 2rem;
        padding: 2rem;
    }

    .landing-header { text-align: center; }

    .logo-mark {
        font-size: 2.5rem;
        color: var(--gold);
        display: block;
        margin-bottom: 0.5rem;
        animation: pulse 3s ease-in-out infinite;
    }

    h1 {
        font-size: 3.5rem;
        font-weight: 900;
        color: var(--text);
        line-height: 1;
    }

    .tagline { margin-top: 0.5rem; }

    .landing-card {
        width: 100%;
        max-width: 520px;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .option-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .section-header {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
    }

    h2 { font-size: 1rem; color: var(--text-mid); }

    .grid-options {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.5rem;
    }

    .grid-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.2rem;
        padding: 0.75rem 0.5rem;
        background: var(--surface-alt);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        cursor: pointer;
        color: var(--text-dim);
        transition: border-color 0.15s, color 0.15s, background 0.15s;
    }

    .grid-btn:hover { border-color: var(--text-muted); color: var(--text-mid); }
    .grid-btn.active { background: #1e1a14; border-color: var(--gold); color: var(--text); }

    .grid-code { font-family: var(--font-mono); font-size: 1rem; font-weight: 500; }
    .grid-sub { font-size: 0.6rem; opacity: 0.6; text-align: center; }

    .diff-options { display: flex; flex-direction: column; gap: 0.5rem; }

    .diff-btn {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.875rem 1rem;
        background: var(--surface-alt);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        cursor: pointer;
        color: var(--text-dim);
        gap: 1rem;
        transition: border-color 0.15s, color 0.15s, background 0.15s;
        text-align: left;
    }

    .diff-btn:hover { border-color: var(--text-muted); color: var(--text-mid); }
    .diff-btn.active { background: #1e1a14; border-color: var(--gold); color: var(--text); }

    .diff-name { font-size: 0.85rem; font-weight: 500; text-transform: capitalize; min-width: 90px; }
    .diff-desc { font-size: 0.7rem; opacity: 0.55; text-align: right; }

    .start-btn { width: 100%; }

    .arrow { font-size: 1.1rem; transition: transform 0.2s ease; }
    .start-btn:hover .arrow { transform: translateX(4px); }

    .landing-footer { font-size: 0.65rem; }

    @media (max-width: 620px) {
        h1 { font-size: 2.5rem; }
        .grid-options { grid-template-columns: repeat(2, 1fr); }
        .diff-btn { align-items: flex-start; flex-direction: column; }
        .diff-desc { text-align: left; }
    }
</style>
