import { PUBLIC_API_URL } from '$env/static/public'
const API_URL = PUBLIC_API_URL

export type Clue = {
    id: number
    type: string
    text: string
    cat1: string
    val1: string
    cat2: string | null
    val2: string | null
    position: number | null
}

export type Puzzle = {
    id: string
    grid: string
    difficulty: string
    categories: string[]
    clues: Clue[]
}

export type HintResponse = {
    category: string
    position: number
    value: string
}

export async function fetchPuzzle(
    grid = '4x5',
    difficulty = 'moderate'
): Promise<Puzzle> {
    const res = await fetch(`${API_URL}/puzzle/?grid=${grid}&difficulty=${difficulty}`)
    if (!res.ok) throw new Error(`Failed to fetch puzzle: ${res.statusText}`)
    return res.json()
}

export async function validateSolution(
    puzzleId: string,
    solution: Record<string, string[]>
): Promise<{ correct: boolean }> {
    const res = await fetch(`${API_URL}/puzzle/${puzzleId}/validate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ solution }),
    })
    if (!res.ok) throw new Error(`Validation failed: ${res.statusText}`)
    return res.json()
}

export async function fetchHint(
    puzzleId: string,
    category: string,
    position: number
): Promise<HintResponse> {
    const res = await fetch(
        `${API_URL}/puzzle/${puzzleId}/hint/?category=${category}&position=${position}`
    )
    if (!res.ok) throw new Error(`Hint failed: ${res.statusText}`)
    return res.json()
}