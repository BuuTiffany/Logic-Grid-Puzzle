<script lang="ts">
    import { onMount, onDestroy } from 'svelte'
    import { goto } from '$app/navigation'
    import { fetchPuzzle, validateSolution, fetchHint } from '$lib/api'
    import GuestNotice from '$lib/GuestNotice.svelte'
    import NamePrompt from '$lib/NamePrompt.svelte'
    import type { Puzzle } from '$lib/api'

    export let data

    let puzzle: Puzzle | null = null
    let loading = true
    let error = ''
    let userGrid: Record<string, string[]> = {}
    let result: 'correct' | 'wrong' | null = null
    let hints: Record<string, Record<number, string>> = {}
    let checking = false
    let dragTarget: { cat: string; pos: number } | null = null
    let startTime: number | null = null
    let solveSeconds = 0
    let showNamePrompt = false
    let elapsed = 0
    let timerInterval: ReturnType<typeof setInterval> | null = null

    $: displayTime = `${Math.floor(elapsed / 60)}:${String(elapsed % 60).padStart(2, '0')}`

    function startTimer() {
        if (timerInterval) clearInterval(timerInterval)
        elapsed = 0
        timerInterval = setInterval(() => {
            if (startTime !== null) elapsed = Math.floor((Date.now() - startTime) / 1000)
        }, 1000)
    }

    function stopTimer() {
        if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
    }

    onDestroy(stopTimer)

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
        startTime = null
        showNamePrompt = false
        stopTimer()
        try {
            puzzle = await fetchPuzzle(grid, difficulty)
            const numCols = parseInt(grid.split('x')[1])
            userGrid = Object.fromEntries(
                puzzle.categories.map(cat => [cat, Array(numCols).fill('')])
            )
            startTime = Date.now()
            startTimer()
        } catch (e) {
            error = (e as Error).message
        } finally {
            loading = false
        }
    }

    function handleCellInput(cat: string, pos: number, value: string) {
        userGrid[cat][pos] = value
        userGrid = { ...userGrid }
        result = null
    }

    function handleClearCell(e: MouseEvent, cat: string, pos: number) {
        e.preventDefault()
        if (isHinted(cat, pos)) return
        handleCellInput(cat, pos, '')
    }

    async function handleValidate() {
        if (!puzzle || checking) return
        checking = true
        try {
            const res = await validateSolution(puzzle.id, userGrid)
            result = res.correct ? 'correct' : 'wrong'
            if (res.correct && startTime !== null) {
                solveSeconds = Math.max(1, Math.round((Date.now() - startTime) / 1000))
                stopTimer()
                elapsed = solveSeconds
                showNamePrompt = true
            }
        } catch (e) {
            error = (e as Error).message
        } finally {
            checking = false
        }
    }

    async function handleHint(cat: string, pos: number) {
        if (!puzzle) return
        try {
            const res = await fetchHint(puzzle.id, cat, pos)
            hints = { ...hints, [cat]: { ...(hints[cat] ?? {}), [pos]: res.value } }
            handleCellInput(cat, pos, res.value)
        } catch (e) {
            error = (e as Error).message
        }
    }

    function isHinted(cat: string, pos: number): boolean {
        return hints[cat]?.[pos] !== undefined
    }

    function isFilled(cat: string, pos: number): boolean {
        return (userGrid[cat]?.[pos] ?? '') !== ''
    }

    $: progress = puzzle
        ? (() => {
            let filled = 0
            let total = 0
            for (const cat of puzzle.categories) {
                for (let i = 0; i < cols; i++) {
                    total++
                    if (isFilled(cat, i)) filled++
                }
            }
            return Math.round((filled / total) * 100)
        })()
        : 0
</script>

<GuestNotice message="You are playing as a guest." />

{#if showNamePrompt && puzzle}
    <NamePrompt
        puzzle_id={puzzle.id}
        grid={puzzle.grid}
        difficulty={puzzle.difficulty}
        solve_time={solveSeconds}
        onClose={() => showNamePrompt = false}
    />
{/if}
<div class="bg-grid"></div>

{#if loading}
    <div class="state-screen">
        <div class="spinner">◈</div>
        <p>Generating puzzle…</p>
    </div>

{:else if error}
    <div class="state-screen">
        <p class="error-text">{error}</p>
        <button class="btn-ghost" on:click={() => loadPuzzle(data.grid, data.difficulty)}>Try again</button>
        <button class="btn-ghost" on:click={() => goto('/')}>← Back</button>
    </div>

{:else if puzzle}
    <div class="layout">

        <!-- Clues panel -->
        <aside class="clues-panel">
            <div class="panel-header">
                <button class="back-btn btn-ghost" on:click={() => goto('/')}>←</button>
                <div>
                    <div class="label-sm">{puzzle.grid} · {puzzle.difficulty}</div>
                    <div class="label-dim">{puzzle.clues.length} clues</div>
                </div>
                <div class="timer" class:timer-done={result === 'correct'}>
                    {displayTime}
                </div>
            </div>

            <h2 class="panel-title">Clues</h2>

            <ol class="clue-list">
                {#each puzzle.clues as clue, i}
                    <li class="clue-item">
                        <span class="clue-num">{i + 1}</span>
                        <span class="clue-text">{clue.text}</span>
                    </li>
                {/each}
            </ol>
            <div class="divider"></div>
        </aside>

        <!-- Puzzle panel -->
        <div class="puzzle-panel">

            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>

            <p class="panel-title">Drag values into cells · Right-click a filled cell to remove</p>

            <div class="grid-wrapper">
                <table class="grid-table">
                    <thead>
                        <tr>
                            <th class="cat-header"></th>
                            {#each Array(cols) as _, i}
                                <th class="house-header">
                                    <span class="label-dim">{i + 1}</span>
                                </th>
                            {/each}
                        </tr>
                    </thead>
                    <tbody>
                        {#each puzzle.categories as cat}
                            <tr>
                                <td class="cat-label">{cat}</td>
                                {#each Array(cols) as _, pos}
                                    <td
                                        class="cell"
                                        class:hinted={isHinted(cat, pos)}
                                        class:filled={isFilled(cat, pos) && !isHinted(cat, pos)}
                                        class:active={dragTarget?.cat === cat && dragTarget?.pos === pos}
                                        on:contextmenu={e => handleClearCell(e, cat, pos)}
                                        on:dragover={e => {
                                            if (!isHinted(cat, pos)) { e.preventDefault(); dragTarget = { cat, pos } }
                                        }}
                                        on:dragleave={() => dragTarget = null}
                                        on:drop={e => {
                                            e.preventDefault()
                                            dragTarget = null
                                            if (isHinted(cat, pos)) return
                                            if (!e.dataTransfer) return
                                            const { cat: srcCat, val } = JSON.parse(e.dataTransfer.getData('text/plain'))
                                            if (srcCat !== cat) return
                                            handleCellInput(cat, pos, val)
                                        }}
                                    >
                                        <div
                                            class="cell-value"
                                            class:hinted-val={isHinted(cat, pos)}
                                            role="listitem"
                                            tabindex="-1"
                                        >
                                            {userGrid[cat]?.[pos] || ''}
                                        </div>
                                        {#if !isHinted(cat, pos) && !isFilled(cat, pos)}
                                            <button
                                                class="hint-btn"
                                                on:click={() => handleHint(cat, pos)}
                                                title="Reveal this cell"
                                            >?</button>
                                        {/if}
                                    </td>
                                {/each}
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>

            <div class="actions">
                <button class="btn-primary" on:click={handleValidate}>
                    {checking ? 'Checking…' : 'Check Solution'}
                </button>
                <button class="btn-ghost" on:click={() => loadPuzzle(data.grid, data.difficulty)}>
                    New Puzzle
                </button>
            </div>

            {#if result === 'correct'}
                <div class="result correct">✓ Correct — well done.</div>
            {:else if result === 'wrong'}
                <div class="result wrong">✗ Not quite — keep going.</div>
            {/if}

            {#if progress < 100}
                <p class="label-dim progress-hint">{progress}% filled — complete the grid to check.</p>
            {/if}

            <div class="values-section">
                <h2 class="panel-title">Values</h2>
                {#if puzzle.values}
                    {#each puzzle.categories as cat}
                        <div class="value-group">
                            <span class="value-cat">{cat}</span>
                            <div class="value-chips">
                                {#each puzzle.values[cat] as val}
                                    {@const isUsed = (userGrid[cat] ?? []).includes(val)}
                                    <span
                                        class="value-chip"
                                        class:used={isUsed}
                                        draggable="true"
                                        role="listitem"
                                        tabindex="-1"
                                        on:dragstart={e => {
                                            if (isUsed) { e.preventDefault(); return }
                                            if (!e.dataTransfer) return
                                            e.dataTransfer.setData('text/plain', JSON.stringify({ cat, val }))
                                            e.dataTransfer.effectAllowed = 'move'
                                        }}
                                    >{val}</span>
                                {/each}
                            </div>
                        </div>
                    {/each}
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
    .drag-hint {
        font-size: 0.7rem;
        margin-top: -0.75rem;
    }

    .values-section {
        display: flex;
        flex-direction: column;
        gap: 0.875rem;
    }

    .value-group {
        display: flex;
        flex-direction: column;
        gap: 0.375rem;
    }

    .value-cat {
        font-size: 0.6rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--gold);
        opacity: 0.8;
    }

    .value-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.3rem;
    }

    .value-chip {
        font-size: 0.65rem;
        padding: 0.2rem 0.5rem;
        background: var(--surface-alt);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text-dim);
        white-space: nowrap;
        transition: opacity 0.15s;
        cursor: grab;
    }

    .value-chip.used {
        opacity: 0.25;
        cursor: default;
        pointer-events: none;
    }

    .value-chip:not(.used):active {
        cursor: grabbing;
    }

    /* ── State screens ── */
    .state-screen {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        color: var(--text-dim);
        font-size: 0.85rem;
        position: relative;
        z-index: 1;
    }

    .error-text { color: var(--error-text); }

    /* ── Two-column layout ── */
    .layout {
        display: grid;
        grid-template-columns: 300px 1fr;
        min-height: 100vh;
        position: relative;
        z-index: 1;
    }

    /* ── Clues panel ── */
    .clues-panel {
        background: #0e0e12;
        border-right: 1px solid var(--border-dim);
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
        overflow-y: auto;
        position: sticky;
        top: 0;
        height: 100vh;
    }

    .panel-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .timer {
        margin-left: auto;
        font-family: var(--font-mono);
        font-size: 1rem;
        font-variant-numeric: tabular-nums;
        color: var(--text-muted);
        letter-spacing: 0.05em;
        transition: color 0.3s;
    }

    .timer-done { color: var(--gold); }

    .back-btn {
        width: 32px;
        height: 32px;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 1rem;
    }

    .panel-title {
        font-size: 1.1rem;
        color: var(--text-mid);
        border-bottom: 1px solid var(--border-dim);
        padding-bottom: 0.75rem;
    }

    .clue-list {
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .clue-item {
        display: flex;
        gap: 0.625rem;
        align-items: flex-start;
        font-size: 0.72rem;
        line-height: 1.5;
        color: var(--text-dim);
    }

    .clue-num {
        color: var(--gold);
        font-size: 0.6rem;
        min-width: 18px;
        padding-top: 0.1em;
        opacity: 0.7;
    }

    .clue-text { flex: 1; }

    /* ── Puzzle panel ── */
    .puzzle-panel {
        padding: 2rem;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        overflow-x: auto;
    }

    /* ── Progress bar ── */
    .progress-bar {
        height: 2px;
        background: var(--border-dim);
        border-radius: 1px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: var(--gold);
        border-radius: 1px;
        transition: width 0.3s ease;
    }

    /* ── Grid table ── */
    .grid-wrapper { overflow-x: auto; }

    .grid-table {
        border-collapse: collapse;
        width: 100%;
        min-width: 500px;
    }

    .cat-header { width: 110px; }

    .house-header {
        text-align: center;
        padding: 0.5rem;
        border-bottom: 1px solid var(--border);
    }

    .cat-label {
        font-size: 0.65rem;
        letter-spacing: 0.1em;
        text-transform: capitalize;
        color: var(--text-muted);
        padding: 0 0.75rem 0 0;
        white-space: nowrap;
        border-right: 1px solid var(--border-dim);
    }

    .cell {
        border: 1px solid var(--border-dim);
        position: relative;
        transition: background 0.15s;
        min-width: 80px;
    }

    .cell:hover { background: var(--surface); }
    .cell.filled { background: #131310; }
    .cell.hinted { background: #1a1a12; }

    .cell.filled:not(.hinted) {
        cursor: context-menu;
    }

    .cell.active {
        background: #16161c;
        border-color: var(--gold);
        border-style: dashed;
    }

    .cell-value {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 2rem;
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--text);
        padding: 0.3rem 1.2rem 0.3rem 0.3rem;
        user-select: none;
    }

    .hinted-val { color: var(--gold); }

    .hint-btn {
        position: absolute;
        top: 50%;
        right: 4px;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: #333;
        cursor: pointer;
        font-size: 0.65rem;
        font-family: var(--font-mono);
        padding: 2px 4px;
        border-radius: 3px;
        transition: color 0.15s;
        line-height: 1;
    }

    .hint-btn:hover { color: var(--gold); }

    /* ── Actions ── */
    .actions {
        display: flex;
        gap: 0.75rem;
        align-items: center;
    }

    .progress-hint { margin-top: -0.5rem; }

    /* ── Responsive ── */
    @media (max-width: 768px) {
        .layout {
            grid-template-columns: 1fr;
            grid-template-rows: auto 1fr;
        }

        .clues-panel {
            position: static;
            height: auto;
            max-height: 40vh;
            border-right: none;
            border-bottom: 1px solid var(--border-dim);
        }
    }
</style>