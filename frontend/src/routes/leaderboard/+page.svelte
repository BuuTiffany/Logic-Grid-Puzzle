
<script lang="ts">
    import './page.css'
    let { data } = $props();

    let searchQuery = $state('');
    let sortBy = $state('time');

    let processedPlayers = $derived.by(() => {
        let list = [...data.players].sort((a, b) => {
            if (sortBy === 'time') {
                const toSec = (t: string) =>
                    t.split(':').reduce((acc, v) => acc * 60 + +v, 0);

                return toSec(a.time) - toSec(b.time);
            } else {
                return new Date(b.date).getTime() - new Date(a.date).getTime();
            }
        });

        const query = searchQuery.toLowerCase();
        console.log("SORT RUN", sortBy);
        return list.filter(p => p.name.toLowerCase().includes(query));
    });

    function toggleSort() {
        sortBy = sortBy === 'time' ? 'date' : 'time';
    }
</script>

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

    <div class="table-wrapper">
        <div class="table-header">
            <div class="col-rank">#</div>
            <div class="col-player">PLAYER</div>
            <div class="col-time">TIME</div>
            <div class="col-date">DATE</div>
            <button class="sort-btn" on:click={toggleSort} title="Toggle Sort">
                {sortBy === 'time' ? 'Sort By: Time' : 'Sort By: Date'}
            </button>
        </div>
        
        <div class="table-body">
            {#each processedPlayers as player, i}
                <div class="table-row" class:is-user={player.name === 'You'}>
                    <div class="col-rank">{i + 1}</div>
                    <div class="col-player">{player.name}</div>
                    <div class="col-time">{player.time}</div>
                    <div class="col-date">{new Date(player.date).toLocaleString('en-CA', {
                                                year: 'numeric',
                                                month: '2-digit',
                                                day: '2-digit',
                                                hour: '2-digit',
                                                minute: '2-digit',
                                                hour12: false
                                            })}
                    </div>
                </div>
            {:else}
                <div class="empty-state">No players found.</div>
            {/each}
        </div>
    </div>
</div>

<style>
/* ── Leaderboard layout ── */
.leaderboard-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 3rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
    position: relative;
    z-index: 1;
}

/* ── Stats grid ── */
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

.search-container input::placeholder {
    color: var(--text-faint);
}

.search-container input:focus {
    border-color: var(--gold);
}

/* ── Table wrapper ── */
.table-wrapper {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

/* ── Table header ── */
.table-header {
    display: grid;
    grid-template-columns: 48px 1fr 100px 160px auto;
    align-items: center;
    padding: 0.65rem 1.25rem;
    background: var(--surface-alt);
    border-bottom: 1px solid var(--border);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* ── Sort button ── */
.sort-btn {
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-dim);
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    padding: 0.3rem 0.6rem;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s;
    white-space: nowrap;
}

.sort-btn:hover {
    border-color: var(--gold);
    color: var(--gold);
}

/* ── Table rows ── */
.table-body {
    display: flex;
    flex-direction: column;
}

.table-row {
    display: grid;
    grid-template-columns: 48px 1fr 100px 160px;
    align-items: center;
    padding: 0.75rem 1.25rem;
    border-bottom: 1px solid var(--border-dim);
    font-size: 0.78rem;
    color: var(--text-dim);
    transition: background 0.1s;
}

.table-row:last-child {
    border-bottom: none;
}

.table-row:hover {
    background: var(--surface-alt);
}

/* ── Highlighted user row ── */
.table-row.is-user {
    background: #1a1610;
    color: var(--text);
}

.table-row.is-user .col-rank {
    color: var(--gold);
    font-weight: 500;
}

.table-row.is-user:hover {
    background: #1e1a12;
}

/* ── Column styles ── */
.col-rank {
    color: var(--text-faint);
    font-size: 0.7rem;
}

.col-player {
    color: var(--text);
}

.col-time {
    font-family: var(--font-mono);
    color: var(--gold-light);
}

.col-date {
    color: var(--text-muted);
    font-size: 0.72rem;
}

/* ── Empty state ── */
.empty-state {
    padding: 3rem;
    text-align: center;
    color: var(--text-faint);
    font-size: 0.78rem;
    letter-spacing: 0.1em;
}

/* ── Responsive ── */
@media (max-width: 600px) {
    .stats-grid {
        grid-template-columns: 1fr 1fr;
    }

    .table-header,
    .table-row {
        grid-template-columns: 36px 1fr 80px;
    }

    .col-date {
        display: none;
    }

    .table-header .col-date {
        display: none;
    }
}
</style>