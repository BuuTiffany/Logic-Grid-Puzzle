import { writable } from 'svelte/store'
import { getCurrentUser, logout as logoutRequest } from '$lib/api'
import type { AuthUser } from '$lib/api'

export const authUser = writable<AuthUser | null>(null)
export const authLoaded = writable(false)

export async function refreshAuth() {
    const user = await getCurrentUser()
    authUser.set(user.authenticated ? user : null)
    authLoaded.set(true)
    return user
}

export async function logoutCurrentUser() {
    await logoutRequest()
    authUser.set(null)
    authLoaded.set(true)
}
