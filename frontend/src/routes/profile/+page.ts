import type { PageLoad } from './$types';

interface Solve {
    puzzle: string;
    size: string;
    difficulty: string;
    time: string;
    date: string;
}

export const load: PageLoad = async ({ fetch }) => {
    /*
    const response = await fetch('/api/profile');
    if (!response.ok) throw new Error('Failed to fetch');
    const data = await response.json();
    return { username: data.username, stats: data.stats, solves: data.solves };
    */
    
    const solves = [
        { puzzle: '4x4 Easy',        size: '4x4', difficulty: 'Easy',        time: '1:10', date: '2026-04-11T22:30:00Z' },
        { puzzle: '4x5 Moderate',    size: '4x5', difficulty: 'Moderate',    time: '2:34', date: '2026-04-10T14:05:00Z' },
        { puzzle: '4x4 Easy',        size: '4x4', difficulty: 'Easy',        time: '1:47', date: '2026-04-08T09:12:00Z' },
        { puzzle: '4x6 Challenging', size: '4x6', difficulty: 'Challenging', time: '5:02', date: '2026-04-05T18:44:00Z' },
        { puzzle: '3x4 Easy',        size: '3x4', difficulty: 'Easy',        time: '0:58', date: '2026-04-04T11:20:00Z' },
        { puzzle: '3x5 Moderate',    size: '3x5', difficulty: 'Moderate',    time: '1:42', date: '2026-04-03T16:33:00Z' },
        { puzzle: '4x5 Easy',        size: '4x5', difficulty: 'Easy',        time: '1:25', date: '2026-04-02T10:15:00Z' },
        { puzzle: '4x6 Moderate',    size: '4x6', difficulty: 'Moderate',    time: '3:18', date: '2026-04-01T13:47:00Z' },
        { puzzle: '4x7 Challenging', size: '4x7', difficulty: 'Challenging', time: '6:45', date: '2026-03-31T09:22:00Z' },
        { puzzle: '3x5 Easy',        size: '3x5', difficulty: 'Easy',        time: '1:03', date: '2026-03-30T15:11:00Z' },
        { puzzle: '4x4 Moderate',    size: '4x4', difficulty: 'Moderate',    time: '2:11', date: '2026-03-29T12:44:00Z' },
        { puzzle: '4x5 Challenging', size: '4x5', difficulty: 'Challenging', time: '4:56', date: '2026-03-28T10:33:00Z' },
        { puzzle: '3x4 Moderate',    size: '3x4', difficulty: 'Moderate',    time: '1:28', date: '2026-03-27T14:05:00Z' },
        { puzzle: '4x7 Moderate',    size: '4x7', difficulty: 'Moderate',    time: '5:23', date: '2026-03-26T11:18:00Z' },
        { puzzle: '3x5 Challenging', size: '3x5', difficulty: 'Challenging', time: '3:42', date: '2026-03-25T08:50:00Z' },
        { puzzle: '4x6 Easy',        size: '4x6', difficulty: 'Easy',        time: '2:09', date: '2026-03-24T16:27:00Z' },
        { puzzle: '4x4 Challenging', size: '4x4', difficulty: 'Challenging', time: '3:15', date: '2026-03-23T12:39:00Z' },
        { puzzle: '3x4 Easy',        size: '3x4', difficulty: 'Easy',        time: '0:45', date: '2026-03-22T09:56:00Z' },
        { puzzle: '4x7 Easy',        size: '4x7', difficulty: 'Easy',        time: '3:38', date: '2026-03-21T14:22:00Z' }
    ];

    // Calculate favorite difficulty
    const difficultyCount: Record<string, number> = {};
    solves.forEach(s => {
        difficultyCount[s.difficulty] = (difficultyCount[s.difficulty] || 0) + 1;
    });
    const favoriteDifficulty = Object.entries(difficultyCount).sort((a, b) => b[1] - a[1])[0][0];

    // Calculate average solve time
    const timeInSeconds = solves.map(s => {
        const [min, sec] = s.time.split(':').map(Number);
        return min * 60 + sec;
    });
    const avgSeconds = Math.round(timeInSeconds.reduce((a, b) => a + b, 0) / timeInSeconds.length);
    const avgMinutes = Math.floor(avgSeconds / 60);
    const avgSecs = avgSeconds % 60;
    const averageTime = `${avgMinutes}:${avgSecs.toString().padStart(2, '0')}`;

    return {
        username: 'You',
        stats: {
            puzzlesSolved: 19,
            favoriteDifficulty,
            averageTime
        },
        solves
    };
};
