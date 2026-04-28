// frontend/src/routes/puzzle/+page.ts
import type { PageLoad } from './$types'

export const load: PageLoad = ({ url }) => {
    const grid = url.searchParams.get('grid') ?? '4x5'
    const difficulty = url.searchParams.get('difficulty') ?? 'moderate'
    console.log('loader got:', grid, difficulty)  // debug
    return { grid, difficulty }
}