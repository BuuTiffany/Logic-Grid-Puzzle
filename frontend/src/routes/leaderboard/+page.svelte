
<script lang="ts">
    import './page.css'
    let { data } = $props();

    const PAGE_SIZE = 10;
    const SIZES = ['3x4', '3x5', '4x4', '4x5', '4x6', '4x7'];
    const DIFFICULTIES = ['Easy', 'Moderate', 'Challenging'];

    let searchQuery   = $state('');
    let sortBy        = $state('time');
    let filterSize    = $state('');
    let filterDiff    = $state('');
    let currentPage   = $state(1);

    let processedPlayers = $derived.by(() => {
        let list = [...data.players].sort((a, b) => {
            if (sortBy === 'time') {
                const toSec = (t: string) =>
                    t.split(':').reduce((acc, v) => acc * 60 + +v, 0);
                return toSec(a.time) - toSec(b.time);
            }
            return new Date(b.date).getTime() - new Date(a.date).getTime();
        });

        const query = searchQuery.toLowerCase();
        return list.filter(p =>
            p.name.toLowerCase().includes(query) &&
            (filterSize === '' || p.size === filterSize) &&
            (filterDiff === '' || p.difficulty === filterDiff)
        );
    });

    $effect(() => { processedPlayers; currentPage = 1; });

    let totalPages     = $derived(Math.max(1, Math.ceil(processedPlayers.length / PAGE_SIZE)));
    let pagePlayers    = $derived(processedPlayers.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE));

    function toggleSort() {
        sortBy = sortBy === 'time' ? 'date' : 'time';
    }
</script>

<div class="bg-grid"></div>
<div class="leaderboard-container">

    <div class="stats-grid">
        <div class="stat-card">
            <span class="stat-label">Total solves</span>
            <span class="stat-value">{data.stats.totalSolves}</span>
        </div>
        <div class="stat-card">
            <span class="stat-label">Your rank</span>
            <span class="stat-value">{data.stats.yourRank}</span>
        </div>
        <div class="stat-card">
            <span class="stat-label">Top %</span>
            <span class="stat-value">{data.stats.topPercent}</span>
        </div>
    </div>

    <div class="search-container">
        <input type="text" placeholder="Search player..." bind:value={searchQuery} />
    </div>

    <div class="controls-bar">
        <div class="filters">
            <select bind:value={filterSize}>
                <option value="">All Sizes</option>
                {#each SIZES as s}
                    <option value={s}>{s}</option>
                {/each}
            </select>
            <select bind:value={filterDiff}>
                <option value="">All Difficulties</option>
                {#each DIFFICULTIES as d}
                    <option value={d}>{d}</option>
                {/each}
            </select>
        </div>
        <button class="sort-btn" onclick={toggleSort}>
            {sortBy === 'time' ? 'Sort By: Time' : 'Sort By: Date'}
        </button>
    </div>

    <div class="table-wrapper">
        <div class="table-header">
            <div class="col-rank">#</div>
            <div class="col-player">Player</div>
            <div class="col-size">Size</div>
            <div class="col-difficulty">Difficulty</div>
            <div class="col-time">Time</div>
            <div class="col-date">Date</div>
        </div>

        <div class="table-body">
            {#each pagePlayers as player, i}
                <div class="table-row" class:is-user={player.name === 'You'}>
                    <div class="col-rank">{(currentPage - 1) * PAGE_SIZE + i + 1}</div>
                    <div class="col-player">{player.name}</div>
                    <div class="col-size">{player.size}</div>
                    <div class="col-difficulty">{player.difficulty}</div>
                    <div class="col-time">{player.time}</div>
                    <div class="col-date">{new Date(player.date).toLocaleString('en-CA', {
                        year: 'numeric', month: '2-digit', day: '2-digit',
                        hour: '2-digit', minute: '2-digit', hour12: false
                    })}</div>
                </div>
            {:else}
                <div class="empty-state">No players found.</div>
            {/each}
        </div>
    </div>

    <div class="pagination">
        <button onclick={() => currentPage = 1}          disabled={currentPage === 1}>«</button>
        <button onclick={() => currentPage -= 1}         disabled={currentPage === 1}>‹</button>
        <span class="page-info">{currentPage} of {totalPages}</span>
        <button onclick={() => currentPage += 1}         disabled={currentPage === totalPages}>›</button>
        <button onclick={() => currentPage = totalPages} disabled={currentPage === totalPages}>»</button>
    </div>

</div>

<style>
/* ── Layout ── */
.leaderboard-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 3rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
    position: relative;
    z-index: 1;
}

/* ── Stats ── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}

.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.25rem 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}

.stat-label {
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.stat-value {
    font-family: var(--font-display);
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--gold);
    line-height: 1;
}

/* ── Search ── */
.search-container input {
    width: 100%;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 0.65rem 1rem;
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 0.8rem;
    outline: none;
    transition: border-color 0.15s;
}

.search-container input::placeholder { color: var(--text-faint); }
.search-container input:focus        { border-color: var(--gold); }

/* ── Controls bar ── */
.controls-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.filters {
    display: flex;
    gap: 0.5rem;
}

.filters select {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.05em;
    padding: 0.3rem 0.6rem;
    cursor: pointer;
    outline: none;
    transition: border-color 0.15s, color 0.15s;
    appearance: none;
    -webkit-appearance: none;
    padding-right: 1.4rem;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23555'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.5rem center;
}

.filters select:hover,
.filters select:focus {
    border-color: var(--gold);
    color: var(--text);
}

/* ── Sort button ── */
.sort-btn {
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    padding: 0.3rem 0.75rem;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s;
    white-space: nowrap;
}

.sort-btn:hover {
    border-color: var(--gold);
    color: var(--gold);
}

/* ── Table ── */
.table-wrapper {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.table-header,
.table-row {
    display: grid;
    grid-template-columns: 48px 1fr 70px 120px 80px 150px;
    align-items: center;
    padding: 0.65rem 1.25rem;
}

.table-header {
    background: var(--surface-alt);
    border-bottom: 1px solid var(--border);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.table-body { display: flex; flex-direction: column; }

.table-row {
    border-bottom: 1px solid var(--border-dim);
    font-size: 0.78rem;
    color: var(--text-dim);
    transition: background 0.1s;
}

.table-row:last-child  { border-bottom: none; }
.table-row:hover       { background: var(--surface-alt); }

.table-row.is-user              { background: #1a1610; color: var(--text); }
.table-row.is-user .col-rank   { color: var(--gold); font-weight: 500; }
.table-row.is-user:hover       { background: #1e1a12; }

/* ── Columns ── */
.col-rank       { color: var(--text-faint); font-size: 0.7rem; }
.col-player     { color: var(--text); }
.col-size       { color: var(--text-dim); font-family: var(--font-mono); font-size: 0.72rem; }
.col-difficulty { color: var(--text-dim); font-size: 0.72rem; }
.col-time       { font-family: var(--font-mono); color: var(--gold-light); }
.col-date       { color: var(--text-muted); font-size: 0.72rem; }

/* ── Empty state ── */
.empty-state {
    padding: 3rem;
    text-align: center;
    color: var(--text-faint);
    font-size: 0.78rem;
    letter-spacing: 0.1em;
}

/* ── Pagination ── */
.pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
}

.pagination button {
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 0.8rem;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s;
}

.pagination button:hover:not(:disabled) {
    border-color: var(--gold);
    color: var(--gold);
}

.pagination button:disabled {
    opacity: 0.25;
    cursor: not-allowed;
}

.page-info {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    padding: 0 0.5rem;
}

/* ── Responsive ── */
@media (max-width: 700px) {
    .stats-grid { grid-template-columns: 1fr 1fr; }

    .table-header,
    .table-row  { grid-template-columns: 36px 1fr 80px; }

    .col-size,
    .col-difficulty,
    .col-date { display: none; }

    .filters select { display: none; }
}
</style>
