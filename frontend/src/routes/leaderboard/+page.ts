import type { PageLoad } from './$types';
import { PUBLIC_API_URL } from '$env/static/public';

export const load: PageLoad = async ({ fetch }) => {
    const response = await fetch(`${PUBLIC_API_URL}/leaderboard/`);
    if (!response.ok) throw new Error('Failed to fetch leaderboard');
    const data = await response.json();
    const players = data.players;
    
    /*const players: { name: string; size: string; difficulty: string; time: string; date: string }[] = [
    { name: "Alice", size: "4x5", difficulty: "Moderate", time: "0:58", date: "2026-04-13T10:23:00Z" },
    { name: "Bob", size: "4x6", difficulty: "Challenging", time: "1:02", date: "2026-04-14T15:45:00Z" },
    { name: "Charlie", size: "3x5", difficulty: "Easy", time: "1:05", date: "2026-04-12T08:12:00Z" },
    { name: "You", size: "4x4", difficulty: "Moderate", time: "1:10", date: "2026-04-08T22:30:00Z" },
    { name: "Eve", size: "4x5", difficulty: "Challenging", time: "1:15", date: "2026-04-10T14:05:00Z" },
    { name: "Frank", size: "3x4", difficulty: "Easy", time: "1:21", date: "2026-04-09T09:17:00Z" },
    { name: "Grace", size: "3x4", difficulty: "Easy", time: "1:23", date: "2026-04-11T16:42:00Z" },
    { name: "Henry", size: "4x5", difficulty: "Moderate", time: "1:31", date: "2026-04-07T11:15:00Z" },
    { name: "Iris", size: "4x6", difficulty: "Challenging", time: "1:45", date: "2026-04-06T09:30:00Z" },
    { name: "Jack", size: "3x5", difficulty: "Easy", time: "1:52", date: "2026-04-05T14:22:00Z" },
    { name: "Kate", size: "4x7", difficulty: "Challenging", time: "2:03", date: "2026-04-04T18:55:00Z" },
    { name: "Leo", size: "4x4", difficulty: "Moderate", time: "2:15", date: "2026-04-03T10:44:00Z" },
    { name: "Mia", size: "3x4", difficulty: "Easy", time: "2:28", date: "2026-04-02T13:12:00Z" },
    { name: "Noah", size: "4x5", difficulty: "Moderate", time: "2:34", date: "2026-04-01T08:20:00Z" },
    { name: "Olivia", size: "4x6", difficulty: "Challenging", time: "2:47", date: "2026-03-31T17:33:00Z" },
    { name: "Paul", size: "3x5", difficulty: "Easy", time: "2:51", date: "2026-03-30T11:05:00Z" },
    { name: "Quinn", size: "4x4", difficulty: "Moderate", time: "3:02", date: "2026-03-29T15:48:00Z" },
    { name: "Rachel", size: "4x7", difficulty: "Challenging", time: "3:15", date: "2026-03-28T09:22:00Z" },
    { name: "Sam", size: "3x4", difficulty: "Easy", time: "3:24", date: "2026-03-27T12:37:00Z" },
    { name: "Tina", size: "4x5", difficulty: "Moderate", time: "3:38", date: "2026-03-26T16:11:00Z" },
    { name: "Uma", size: "4x6", difficulty: "Challenging", time: "3:45", date: "2026-03-25T10:29:00Z" },
    { name: "Victor", size: "3x5", difficulty: "Easy", time: "3:56", date: "2026-03-24T14:05:00Z" },
    { name: "Wendy", size: "4x4", difficulty: "Moderate", time: "4:03", date: "2026-03-23T11:18:00Z" },
    { name: "Xander", size: "4x7", difficulty: "Challenging", time: "4:18", date: "2026-03-22T13:42:00Z" },
    { name: "Yara", size: "3x4", difficulty: "Easy", time: "4:22", date: "2026-03-21T09:11:00Z" },
    { name: "Zoe", size: "4x5", difficulty: "Moderate", time: "4:31", date: "2026-03-20T15:33:00Z" },
    { name: "Aaron", size: "4x6", difficulty: "Challenging", time: "4:44", date: "2026-03-19T10:55:00Z" },
    { name: "Bella", size: "3x5", difficulty: "Easy", time: "4:52", date: "2026-03-18T12:24:00Z" },
    { name: "Chris", size: "4x4", difficulty: "Moderate", time: "5:01", date: "2026-03-17T08:40:00Z" },
    { name: "Dana", size: "4x7", difficulty: "Challenging", time: "5:15", date: "2026-03-16T14:18:00Z" },
    { name: "Ethan", size: "3x4", difficulty: "Easy", time: "5:23", date: "2026-03-15T11:02:00Z" },
    { name: "Fiona", size: "4x5", difficulty: "Moderate", time: "5:34", date: "2026-03-14T16:27:00Z" },
    { name: "Gabriel", size: "4x6", difficulty: "Challenging", time: "5:47", date: "2026-03-13T09:38:00Z" },
    { name: "Hannah", size: "3x5", difficulty: "Easy", time: "5:55", date: "2026-03-12T13:56:00Z" },
    { name: "Isaac", size: "4x4", difficulty: "Moderate", time: "6:04", date: "2026-03-11T10:19:00Z" },
    { name: "Jade", size: "4x7", difficulty: "Challenging", time: "6:18", date: "2026-03-10T15:44:00Z" },
    { name: "Kevin", size: "3x4", difficulty: "Easy", time: "6:26", date: "2026-03-09T11:32:00Z" },
    { name: "Luna", size: "4x5", difficulty: "Moderate", time: "6:39", date: "2026-03-08T14:07:00Z" },
    { name: "Marcus", size: "4x6", difficulty: "Challenging", time: "6:51", date: "2026-03-07T09:15:00Z" },
    { name: "Nina", size: "3x5", difficulty: "Easy", time: "6:58", date: "2026-03-06T12:48:00Z" },
    { name: "Oscar", size: "4x4", difficulty: "Moderate", time: "7:09", date: "2026-03-05T10:22:00Z" },
    { name: "Piper", size: "4x7", difficulty: "Challenging", time: "7:22", date: "2026-03-04T16:33:00Z" },
    { name: "Quinn2", size: "3x4", difficulty: "Easy", time: "7:31", date: "2026-03-03T11:51:00Z" },
    { name: "Ryan", size: "4x5", difficulty: "Moderate", time: "7:43", date: "2026-03-02T14:26:00Z" },
    { name: "Sophia", size: "4x6", difficulty: "Challenging", time: "7:56", date: "2026-03-01T09:44:00Z" },
    { name: "Thomas", size: "3x5", difficulty: "Easy", time: "8:04", date: "2026-02-28T13:19:00Z" },
    { name: "Ursula", size: "4x4", difficulty: "Moderate", time: "8:15", date: "2026-02-27T10:41:00Z" },
    { name: "Vincent", size: "4x7", difficulty: "Challenging", time: "8:28", date: "2026-02-26T15:12:00Z" },
    { name: "Willa", size: "3x4", difficulty: "Easy", time: "8:36", date: "2026-02-25T12:05:00Z" },
    { name: "Xander2", size: "4x5", difficulty: "Moderate", time: "8:47", date: "2026-02-24T14:39:00Z" },
    { name: "Yasmin", size: "4x6", difficulty: "Challenging", time: "9:01", date: "2026-02-23T09:52:00Z" },
    { name: "Zachary", size: "3x5", difficulty: "Easy", time: "9:09", date: "2026-02-22T13:28:00Z" }
    ]; */

    const timeToSeconds = (t: string) => t.split(':').reduce((acc, v) => acc * 60 + +v, 0);
    const sortedByTime = [...players].sort((a, b) => timeToSeconds(a.time) - timeToSeconds(b.time));
    const yourRankIndex = sortedByTime.findIndex(p => p.name === 'You') + 1;
    const topPercent = Math.round((yourRankIndex / players.length) * 100 * 10) / 10;
    return {
        stats: {
            totalSolves: players.length.toString(),
            yourRank: `#${yourRankIndex}`,
            topPercent: `${topPercent}%`
        },
        players
    };
};