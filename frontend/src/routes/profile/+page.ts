import type { PageLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { fetchProfile } from '$lib/api';

export const ssr = false;

export const load: PageLoad = async () => {
    let profile;
    try {
        profile = await fetchProfile();
    } catch {
        throw redirect(302, '/');
    }

    const difficultyCount: Record<string, number> = {};
    profile.solves.forEach((solve) => {
        difficultyCount[solve.difficulty] = (difficultyCount[solve.difficulty] || 0) + 1;
    });

    const favoriteDifficulty = Object.entries(difficultyCount).sort((a, b) => b[1] - a[1])[0]?.[0] ?? 'None';
    const timeInSeconds = profile.solves.map((solve) => {
        const [min, sec] = solve.time.split(':').map(Number);
        return min * 60 + sec;
    });
    const avgSeconds = timeInSeconds.length
        ? Math.round(timeInSeconds.reduce((a, b) => a + b, 0) / timeInSeconds.length)
        : 0;
    const averageTime = `${Math.floor(avgSeconds / 60)}:${String(avgSeconds % 60).padStart(2, '0')}`;

    return {
        username: profile.username,
        stats: {
            puzzlesSolved: profile.solves.length,
            favoriteDifficulty,
            averageTime,
        },
        solves: profile.solves,
    };
};
