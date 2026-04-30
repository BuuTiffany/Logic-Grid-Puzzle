import { PUBLIC_API_URL } from '$env/static/public'
const API_URL = PUBLIC_API_URL

async function readResponse<T>(res: Response, fallback: string): Promise<T> {
    const data = await res.json().catch(() => ({}))
    if (!res.ok) throw new Error(data.error ?? fallback)
    return data
}

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
    clue_limit: number
    categories: string[]
    values: Record<string, string[]>
    clues: Clue[]
}

export type HintResponse = {
    category: string
    position: number
    value: string
}

export type AuthUser = {
    authenticated: boolean
    id?: number
    email?: string
    username: string | null
    needs_username: boolean
}

export type GlobalStats = {
    puzzlesSolved: number
    puzzlesAttempted: number
    registeredUsers: number
    anonymousPlayers: number
    mostPopularGrid: {
        grid: string
        plays: number
    }
    averageSolveTimeByDifficulty: {
        difficulty: string
        time: string
        seconds: number
    }[]
    fastestSolve: {
        seconds: number
        time: string
        grid: string
        difficulty: string
        username: string
    }
}

export async function fetchPuzzle(
    grid = '4x5',
    difficulty = 'moderate'
): Promise<Puzzle> {
    const res = await fetch(`${API_URL}/puzzle/?grid=${grid}&difficulty=${difficulty}`)
    return readResponse<Puzzle>(res, `Failed to fetch puzzle: ${res.statusText}`)
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
    return readResponse<{ correct: boolean }>(res, `Validation failed: ${res.statusText}`)
}

export async function submitSolve(payload: {
    username?: string
    puzzle_id: string
    grid: string
    difficulty: string
    solve_time: number
}): Promise<{ saved: boolean }> {
    const res = await fetch(`${API_URL}/solves/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
    })
    return readResponse<{ saved: boolean }>(res, `Submit failed: ${res.statusText}`)
}

export async function fetchHint(
    puzzleId: string,
    category: string,
    position: number
): Promise<HintResponse> {
    const res = await fetch(
        `${API_URL}/puzzle/${puzzleId}/hint/?category=${category}&position=${position}`
    )
    return readResponse<HintResponse>(res, `Hint failed: ${res.statusText}`)
}

export async function getCurrentUser(): Promise<AuthUser> {
    const res = await fetch(`${API_URL}/auth/me/`, { credentials: 'include' })
    return readResponse<AuthUser>(res, 'Failed to load user')
}

export async function signup(email: string, password: string): Promise<AuthUser> {
    const res = await fetch(`${API_URL}/auth/signup/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
    })
    return readResponse<AuthUser>(res, 'Signup failed')
}

export async function login(email: string, password: string): Promise<AuthUser> {
    const res = await fetch(`${API_URL}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
    })
    return readResponse<AuthUser>(res, 'Login failed')
}

export async function logout(): Promise<void> {
    const res = await fetch(`${API_URL}/auth/logout/`, {
        method: 'POST',
        credentials: 'include',
    })
    await readResponse(res, 'Logout failed')
}

export async function setAccountUsername(username: string): Promise<AuthUser> {
    const res = await fetch(`${API_URL}/auth/username/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username }),
    })
    return readResponse<AuthUser>(res, 'Username save failed')
}

export async function fetchProfile(): Promise<{
    username: string
    solves: { puzzle: string; size: string; difficulty: string; time: string; date: string }[]
}> {
    const res = await fetch(`${API_URL}/profile/`, { credentials: 'include' })
    return readResponse(res, 'Failed to fetch profile')
}

export async function fetchGlobalStats(): Promise<GlobalStats> {
    const res = await fetch(`${API_URL}/stats/`)
    return readResponse(res, 'Failed to fetch stats')
}
