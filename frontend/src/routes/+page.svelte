<script lang="ts">
    import { goto } from '$app/navigation'

    let { data } = $props()

    const coreStats = $derived([
        { label: 'Puzzles solved', value: data.stats.puzzlesSolved },
        { label: 'Puzzles attempted', value: data.stats.puzzlesAttempted },
        { label: 'Registered users', value: data.stats.registeredUsers },
        { label: 'Anonymous players', value: data.stats.anonymousPlayers },
    ])
</script>

<div class="bg-grid"></div>

<main class="home">
    <section class="hero">
        <div class="logo-mark">◈</div>
        <h1>Logic Grid</h1>
        <p class="tagline">Deduce. Place. Solve.</p>
        <button class="btn-primary start-btn" onclick={() => goto('/puzzles')}>
            <span>Choose Puzzle</span>
            <span>→</span>
        </button>
    </section>

    <section class="stats-panel">
        <div class="stat-grid">
            {#each coreStats as stat}
                <div class="stat-card">
                    <span class="stat-label">{stat.label}</span>
                    <span class="stat-value">{stat.value}</span>
                </div>
            {/each}
        </div>

        <div class="detail-grid">
            <div class="detail-card">
                <span class="stat-label">Most popular grid</span>
                <span class="detail-value">{data.stats.mostPopularGrid.grid}</span>
                <span class="detail-sub">{data.stats.mostPopularGrid.plays} solves</span>
            </div>

            <div class="detail-card">
                <span class="stat-label">Fastest solve</span>
                <span class="detail-value">{data.stats.fastestSolve.time}</span>
                <span class="detail-sub">
                    {data.stats.fastestSolve.username} · {data.stats.fastestSolve.grid} · {data.stats.fastestSolve.difficulty}
                </span>
            </div>

            <div class="detail-card avg-card">
                <span class="stat-label">Average solve time</span>
                <div class="avg-list">
                    {#each data.stats.averageSolveTimeByDifficulty as item}
                        <div class="avg-row">
                            <span>{item.difficulty}</span>
                            <strong>{item.time}</strong>
                        </div>
                    {:else}
                        <div class="avg-row">
                            <span>No solves yet</span>
                            <strong>0:00</strong>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    </section>
</main>

<style>
    .home {
        position: relative;
        z-index: 1;
        min-height: calc(100vh - 52px);
        display: grid;
        grid-template-columns: minmax(280px, 0.85fr) minmax(360px, 1.15fr);
        align-items: center;
        gap: 3rem;
        max-width: 1120px;
        margin: 0 auto;
        padding: 4rem 2rem;
    }

    .hero {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .logo-mark {
        font-size: 2.8rem;
        color: var(--gold);
        animation: pulse 3s ease-in-out infinite;
    }

    h1 {
        font-size: 4rem;
        font-weight: 900;
        color: var(--text);
        line-height: 1;
    }

    .tagline {
        font-size: 0.78rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--text-muted);
    }

    .start-btn {
        min-width: 220px;
        margin-top: 0.75rem;
    }

    .stats-panel {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .stat-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
    }

    .stat-card,
    .detail-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.15rem 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
    }

    .stat-label {
        font-size: 0.6rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--text-muted);
    }

    .stat-value {
        font-family: var(--font-display);
        font-size: 2rem;
        font-weight: 700;
        color: var(--gold);
        line-height: 1;
    }

    .detail-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
    }

    .avg-card {
        grid-column: 1 / -1;
    }

    .detail-value {
        font-family: var(--font-display);
        font-size: 1.6rem;
        color: var(--text);
        line-height: 1.1;
    }

    .detail-sub {
        font-size: 0.72rem;
        color: var(--text-dim);
    }

    .avg-list {
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
    }

    .avg-row {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        color: var(--text-dim);
        font-size: 0.78rem;
    }

    .avg-row strong {
        color: var(--gold-light);
        font-weight: 500;
    }

    @media (max-width: 820px) {
        .home {
            grid-template-columns: 1fr;
            align-items: start;
            gap: 2rem;
            padding: 3rem 1.25rem;
        }

        h1 { font-size: 3rem; }
    }

    @media (max-width: 520px) {
        .stat-grid,
        .detail-grid {
            grid-template-columns: 1fr;
        }

        .avg-card {
            grid-column: auto;
        }
    }
</style>
