import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch }) => {
    /*
    const response = await fetch('http://127.0.0.1:8000/api/user/');
    if (!response.ok) return { username: null };
    const data = await response.json();
    return { username: data.username ?? null };
    */
    return { username: 'KonoDioDa' };
};
