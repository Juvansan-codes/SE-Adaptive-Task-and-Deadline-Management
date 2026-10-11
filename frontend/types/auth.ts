/**
 * Authentication types and interfaces
 * Designed to cleanly abstract mock authentication and future API endpoints.
 */

export interface User {
  id: string
  name: string
  email: string
  createdAt: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
  confirmPassword: string
}

export type AuthSuccessResult = {
  success: true
  user: User
  message: string
}

export type AuthErrorResult = {
  success: false
  error: string
  fieldErrors?: Record<string, string>
}

export type AuthResult = AuthSuccessResult | AuthErrorResult
