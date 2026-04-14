
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

