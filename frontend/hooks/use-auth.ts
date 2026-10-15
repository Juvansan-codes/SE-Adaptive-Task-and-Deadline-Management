"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { useQueryClient } from "@tanstack/react-query"
import { supabase } from "@/lib/supabase"
import { authService } from "@/services/api/auth"
import type { User, LoginCredentials, RegisterPayload, AuthResult } from "@/types/auth"

export function useAuth() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [user, setUser] = React.useState<User | null>(null)
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    let mounted = true

    // Check active session on mount
    authService.getCurrentUser().then((currentUser) => {
      if (mounted) {
        setUser(currentUser)
        setLoading(false)
      }
    })

    // Listen to Supabase auth events
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!mounted) return

      if (session?.user) {
        const metadata = session.user.user_metadata || {}
        const name =
          (metadata.name as string) ||
          (metadata.full_name as string) ||
          session.user.email?.split("@")[0] ||
          "User"

        setUser({
          id: session.user.id,
          name,
          email: session.user.email || "",
          createdAt: session.user.created_at || new Date().toISOString(),
        })
      } else {
        setUser(null)
      }
      setLoading(false)
    })

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [])

  const login = async (credentials: LoginCredentials): Promise<AuthResult> => {
    const result = await authService.login(credentials)
    if (result.success) {
      setUser(result.user)
      queryClient.clear()
    }
    return result
  }

  const register = async (payload: RegisterPayload): Promise<AuthResult> => {
    const result = await authService.register(payload)
    if (result.success) {
      setUser(result.user)
      queryClient.clear()
    }
    return result
  }

  const logout = async () => {
    await authService.logout()
    setUser(null)
    queryClient.clear()
    router.push("/login")
  }

  return {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  }
}
