<script lang="ts">
    import { onMount } from 'svelte'
    import { fetchPuzzle, validateSolution, fetchHint } from '$lib/api'
    import type { Puzzle } from '$lib/api'

    export let data

    let puzzle: Puzzle | null = null
    let loading = true
    let error = ''
    let userGrid: Record<string, string[]> = {}
    let result: 'correct' | 'wrong' | null = null
    let hints: Record<string, Record<number, string>> = {}

    // Derive cols directly from data, not from puzzle
    // This way it's always correct before loadPuzzle runs
    $: cols = parseInt(data.grid.split('x')[1])

    onMount(() => {
        loadPuzzle(data.grid, data.difficulty)
    })

    async function loadPuzzle(grid: string, difficulty: string) {
        loading = true
        error = ''
        result = null
        hints = {}
        puzzle = null
        try {
            puzzle = await fetchPuzzle(grid, difficulty)
            const numCols = parseInt(grid.split('x')[1])
            userGrid = Object.fromEntries(
                puzzle.categories.map(cat => [cat, Array(numCols).fill('')])
            )
        } catch (e) {
            error = (e as Error).message
        } finally {
            loading = false
        }
    }

    function handleCellInput(cat: string, pos: number, value: string) {
        userGrid[cat][pos] = value
        userGrid = { ...userGrid }   // trigger reactivity
    }

    async function handleValidate() {
        if (!puzzle) return
        try {
            const res = await validateSolution(puzzle.id, userGrid)
            result = res.correct ? 'correct' : 'wrong'
        } catch (e) {
            error = (e as Error).message
        }
    }

    async function handleHint(cat: string, pos: number) {
        if (!puzzle) return
        try {
            const res = await fetchHint(puzzle.id, cat, pos)
            hints = {
                ...hints,
                [cat]: { ...(hints[cat] ?? {}), [pos]: res.value }
            }
            // also fill the cell
            handleCellInput(cat, pos, res.value)
        } catch (e) {
            error = (e as Error).message
        }
    }
</script>

{#if loading}
    <p>Loading puzzle...</p>

{:else if error}
    <p class="error">{error}</p>
    <button on:click={loadPuzzle}>Retry</button>

{:else if puzzle}
    <div class="puzzle">
        <header>
            <h1>Logic Puzzle</h1>
            <p>{puzzle.grid} · {puzzle.difficulty}</p>
            <button on:click={loadPuzzle}>New Puzzle</button>
        </header>

        <!-- Clues -->
        <section class="clues">
            <h2>Clues</h2>
            <ol>
                {#each puzzle.clues as clue}
                    <li>{clue.text}</li>
                {/each}
            </ol>
        </section>

        <!-- Grid -->
        <section class="grid">
            <h2>Your Solution</h2>
            <table>
                <thead>
                    <tr>
                        <th></th>
                        {#each Array(cols) as _, i}
                            <th>House {i + 1}</th>
                        {/each}
                    </tr>
                </thead>
                <tbody>
                    {#each puzzle.categories as cat}
                        <tr>
                            <td class="category-label">{cat}</td>
                            {#each Array(cols) as _, pos}
                                <td class="cell">
                                    <input
                                        type="text"
                                        value={userGrid[cat]?.[pos] ?? ''}
                                        on:input={e =>
                                            handleCellInput(cat, pos, e.currentTarget.value)
                                        }
                                        class:hinted={hints[cat]?.[pos] !== undefined}
                                    />
                                    <button
                                        class="hint-btn"
                                        on:click={() => handleHint(cat, pos)}
                                        title="Get hint"
                                    >?</button>
                                </td>
                            {/each}
                        </tr>
                    {/each}
                </tbody>
            </table>
        </section>

        <!-- Validate -->
        <section class="actions">
            <button on:click={handleValidate}>Check Solution</button>
            {#if result === 'correct'}
                <p class="success">✓ Correct!</p>
            {:else if result === 'wrong'}
                <p class="error">✗ Not quite — keep trying.</p>
            {/if}
        </section>
    </div>
{/if}

<style>
    .puzzle { max-width: 900px; margin: 0 auto; padding: 1rem; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 0.5rem; text-align: center; }
    .category-label { font-weight: bold; text-align: left; text-transform: capitalize; }
    .cell { position: relative; }
    input { width: 90px; border: none; text-align: center; background: transparent; }
    input.hinted { background: #fefce8; }
    .hint-btn { font-size: 0.7rem; cursor: pointer; }
    .success { color: green; font-weight: bold; }
    .error { color: red; }
    ol { line-height: 2; }
</style>