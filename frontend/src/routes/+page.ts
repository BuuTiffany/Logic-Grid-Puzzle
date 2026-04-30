import type { PageLoad } from './$types';
import { fetchGlobalStats } from '$lib/api';

export const load: PageLoad = async () => {
    const stats = await fetchGlobalStats();
    return { stats };
};
