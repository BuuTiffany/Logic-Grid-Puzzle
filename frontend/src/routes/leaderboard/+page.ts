import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
    /*
    const response = await fetch('');
    if (!response.ok) throw new Error('Failed to fetch');
    const data = await response.json();
    return { stats: data.stats, players: data.players };
    */
    return {
        stats: {
            totalSolves: "1,284",
            yourRank: "#4",
            topPercent: "0.5%"
        },
        players: [
        { name: "Alice", time: "0:58", date: "2026-04-14T10:23:00Z" },
        { name: "Bob", time: "1:02", date: "2026-04-13T15:45:00Z" },
        { name: "Charlie", time: "1:05", date: "2026-04-12T08:12:00Z" },
        { name: "You", time: "1:10", date: "2026-04-11T22:30:00Z" },
        { name: "Eve", time: "1:15", date: "2026-04-10T14:05:00Z" },
        { name: "Frank", time: "1:21", date: "2026-04-09T09:17:00Z" }
        ]
    };

};