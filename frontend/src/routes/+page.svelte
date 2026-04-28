<script lang="ts">
    import { goto } from '$app/navigation'

    const GRIDS = ['3x4', '3x5', '4x4', '4x5', '4x6', '4x7']
    const DIFFICULTIES = ['easy', 'moderate', 'challenging']

    let selectedGrid = '4x5'
    let selectedDifficulty = 'moderate'

    function startPuzzle() {
        goto(`/puzzle?grid=${selectedGrid}&difficulty=${selectedDifficulty}`)
    }
</script>

<main>
    <h1>Logic Grid Puzzles</h1>
    <p>Place each value in the correct house using the clues provided.</p>

    <section class="options">
        <div class="option-group">
            <h2>Grid Size</h2>
            <p class="hint">Rows × Houses — more rows means more categories to solve.</p>
            <div class="chips">
                {#each GRIDS as grid}
                    <button
                        class="chip"
                        class:selected={selectedGrid === grid}
                        on:click={() => selectedGrid = grid}
                    >
                        {grid}
                    </button>
                {/each}
            </div>
        </div>

        <div class="option-group">
            <h2>Difficulty</h2>
            <p class="hint">Controls how many clues are given.</p>
            <div class="chips">
                {#each DIFFICULTIES as diff}
                    <button
                        class="chip"
                        class:selected={selectedDifficulty === diff}
                        on:click={() => selectedDifficulty = diff}
                    >
                        {diff}
                    </button>
                {/each}
            </div>
        </div>
    </section>

    <button class="start" on:click={startPuzzle}>
        Start Puzzle
    </button>
</main>

<style>
    main {
        max-width: 600px;
        margin: 4rem auto;
        padding: 1rem;
        text-align: center;
    }
    h1 { font-size: 2rem; margin-bottom: 0.5rem; }
    p.hint { color: #666; font-size: 0.875rem; margin: 0.25rem 0 1rem; }

    .options { display: flex; flex-direction: column; gap: 2rem; margin: 2rem 0; }
    .option-group { text-align: left; }
    .option-group h2 { font-size: 1rem; margin-bottom: 0.25rem; }

    .chips { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .chip {
        padding: 0.4rem 1rem;
        border: 2px solid #ccc;
        border-radius: 999px;
        background: white;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.15s;
    }
    .chip:hover { border-color: #888; }
    .chip.selected { border-color: #3b82f6; background: #eff6ff; color: #1d4ed8; font-weight: 600; }

    .start {
        padding: 0.75rem 2.5rem;
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1.1rem;
        cursor: pointer;
        transition: background 0.15s;
    }
    .start:hover { background: #2563eb; }
</style>