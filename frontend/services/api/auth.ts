/**
 * Supabase Authentication Service
 * Implements IAuthService against real Supabase Auth endpoints.
 */

import { supabase } from "@/lib/supabase"
import type {
  LoginCredentials,
  RegisterPayload,
  AuthResult,
  User,
} from "@/types/auth"

export interface IAuthService {
  login(credentials: LoginCredentials): Promise<AuthResult>
  register(payload: RegisterPayload): Promise<AuthResult>
  logout(): Promise<void>
  getCurrentUser(): Promise<User | null>
}

/**
 * Maps Supabase User entity to application User interface.
 */
function mapSupabaseUser(sbUser: {
  id: string
  email?: string
  user_metadata?: Record<string, unknown>
  created_at?: string
}): User {
  const metadata = sbUser.user_metadata || {}
  const name =
    (metadata.name as string) ||
    (metadata.full_name as string) ||
    sbUser.email?.split("@")[0] ||
    "User"

  return {
    id: sbUser.id,
    name,
    email: sbUser.email || "",
    createdAt: sbUser.created_at || new Date().toISOString(),
  }
}

export const authService: IAuthService = {
  /**
   * Authenticate user with Supabase email and password.
   */
  async login(credentials: LoginCredentials): Promise<AuthResult> {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: credentials.email.trim().toLowerCase(),
        password: credentials.password,
      })

      if (error) {
        let userMessage = error.message
        if (error.message.includes("Invalid login credentials")) {
          userMessage = "Invalid email or password. Please verify your credentials."
        } else if (error.message.includes("Email not confirmed")) {
          userMessage =
            "Email not yet confirmed. Please verify your email inbox before logging in."
        }
        return {
          success: false,
          error: userMessage,
        }
      }

      if (!data.user) {
        return {
          success: false,
          error: "Authentication failed. No user was returned.",
        }
      }

      return {
        success: true,
        user: mapSupabaseUser(data.user),
        message: "Successfully signed in.",
      }
    } catch {
      return {
        success: false,
        error: "Unable to connect to authentication server. Please try again.",
      }
    }
  },

  /**
   * Register a new user with Supabase Auth.
   */
  async register(payload: RegisterPayload): Promise<AuthResult> {
    try {
      const email = payload.email.trim().toLowerCase()
      const name = payload.name.trim()

      const { data, error } = await supabase.auth.signUp({
        email,
        password: payload.password,
        options: {
          data: {
            name,
            full_name: name,
          },
        },
      })

      if (error) {
        let userMessage = error.message
        const fieldErrors: Record<string, string> = {}

        if (error.message.toLowerCase().includes("already registered")) {
          userMessage = "An account with this email address already exists."
          fieldErrors.email = "Email address is already registered."
        }

        return {
          success: false,
          error: userMessage,
          fieldErrors: Object.keys(fieldErrors).length > 0 ? fieldErrors : undefined,
        }
      }

      if (!data.user) {
        return {
          success: false,
          error: "Registration failed. Please try again.",
        }
      }

      const user = mapSupabaseUser(data.user)

      // Check if session was returned or if email confirmation is required
      const message = data.session
        ? "Account created successfully! Redirecting to dashboard..."
        : "Account created! Please check your email to confirm your account."

      return {
        success: true,
        user,
        message,
      }
    } catch {
      return {
        success: false,
        error: "An unexpected error occurred during registration.",
      }
    }
  },

  /**
   * Terminate current Supabase session.
   */
  async logout(): Promise<void> {
    await supabase.auth.signOut()
  },

  /**
   * Retrieve active authenticated user if session exists.
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (!user) return null
      return mapSupabaseUser(user)
    } catch {
      return null
    }
  },
}
