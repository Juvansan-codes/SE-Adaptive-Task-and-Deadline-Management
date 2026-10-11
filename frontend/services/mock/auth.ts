/**
 * ==============================================================================
 * MOCK AUTHENTICATION SERVICE
 * ==============================================================================
 * DISCLAIMER:
 * This service is an asynchronous MOCK intended exclusively for frontend UI
 * verification, form validation testing, and rapid prototyping.
 * 
 * - No real passwords or sensitive credentials are saved, transmitted, or logged.
 * - No real JWT, session cookies, database queries, or FastAPI endpoints are invoked.
 * - This abstraction implements a clean service interface (IAuthService) that can
 *   be seamlessly replaced by an actual backend API client in future phases
 *   without altering form or page components.
 * ==============================================================================
 */

import type {
  LoginCredentials,
  RegisterPayload,
  AuthResult,
  User,
} from "@/types/auth"

export interface IAuthService {
  login(credentials: LoginCredentials): Promise<AuthResult>
  register(payload: RegisterPayload): Promise<AuthResult>
}

// Simulated network latency
const simulateLatency = (ms: number = 750): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms))

// In-memory registered emails for mock duplicate checks during session
const MOCK_REGISTERED_EMAILS = new Set<string>([
  "user@example.com",
  "demo@example.com",
  "exists@example.com",
])

export const mockAuthService: IAuthService = {
  /**
   * Simulates asynchronous user login
   */
  async login(credentials: LoginCredentials): Promise<AuthResult> {
    await simulateLatency(700)

    const normalizedEmail = credentials.email.trim().toLowerCase()

    // Deterministic simulation scenarios for testing
    if (normalizedEmail === "invalid@example.com") {
      return {
        success: false,
        error: "Invalid email or password. Please verify your credentials.",
      }
    }

    if (normalizedEmail === "locked@example.com") {
      return {
        success: false,
        error: "This account has been temporarily locked due to policy restrictions.",
      }
    }

    // Standard credential check simulation:
    // If the email is known and password is at least 6 chars, or any valid email
    if (credentials.password.length < 6) {
      return {
        success: false,
        error: "Invalid email or password. Please verify your credentials.",
      }
    }

    const mockUser: User = {
      id: `usr_mock_${Math.random().toString(36).substring(2, 9)}`,
      name: normalizedEmail.split("@")[0].replace(/[._]/g, " ") || "Demo User",
      email: normalizedEmail,
      createdAt: new Date().toISOString(),
    }

    return {
      success: true,
      user: mockUser,
      message: "Successfully authenticated (Mock Session).",
    }
  },

  /**
   * Simulates asynchronous user registration
   */
  async register(payload: RegisterPayload): Promise<AuthResult> {
    await simulateLatency(800)

    const normalizedEmail = payload.email.trim().toLowerCase()

    // Test duplicate email simulation
    if (MOCK_REGISTERED_EMAILS.has(normalizedEmail)) {
      return {
        success: false,
        error: "An account with this email address already exists.",
        fieldErrors: {
          email: "Email address is already registered.",
        },
      }
    }

    // Add to in-memory set for subsequent duplicate checks
    MOCK_REGISTERED_EMAILS.add(normalizedEmail)

    const mockUser: User = {
      id: `usr_mock_${Math.random().toString(36).substring(2, 9)}`,
      name: payload.name.trim(),
      email: normalizedEmail,
      createdAt: new Date().toISOString(),
    }

    return {
      success: true,
      user: mockUser,
      message: "Account created successfully (Mock Registration).",
    }
  },
}
