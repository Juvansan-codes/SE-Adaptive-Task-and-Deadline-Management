/**
 * Centralized HTTP Client for FastAPI REST Endpoints
 * Automatically attaches Supabase JWT access tokens and formats error responses.
 */

import { API_BASE_URL } from "./config"
import { getAccessToken } from "@/lib/supabase"

export class ApiClientError extends Error {
  status: number
  data?: unknown

  constructor(message: string, status: number, data?: unknown) {
    super(message)
    this.name = "ApiClientError"
    this.status = status
    this.data = data
  }
}

export interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown
  params?: Record<string, string | number | boolean | undefined | null>
}

/**
 * Format query parameter strings from dictionary.
 */
function buildQueryString(
  params?: Record<string, string | number | boolean | undefined | null>
): string {
  if (!params) return ""
  const searchParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.append(key, String(value))
    }
  }
  const qs = searchParams.toString()
  return qs ? `?${qs}` : ""
}

/**
 * Safe error message extractor from FastAPI error payloads.
 */
function extractErrorMessage(status: number, data: unknown): string {
  if (data && typeof data === "object") {
    const errorObj = data as Record<string, unknown>

    // 1. { detail: { message: "..." } }
    if (
      errorObj.detail &&
      typeof errorObj.detail === "object" &&
      !Array.isArray(errorObj.detail)
    ) {
      const detailObj = errorObj.detail as Record<string, unknown>
      if (typeof detailObj.message === "string") {
        return detailObj.message
      }
    }

    // 2. { detail: "string" }
    if (typeof errorObj.detail === "string") {
      return errorObj.detail
    }

    // 3. Pydantic validation errors: { detail: [{ loc: [...], msg: "..." }] }
    if (Array.isArray(errorObj.detail) && errorObj.detail.length > 0) {
      const firstErr = errorObj.detail[0] as Record<string, unknown>
      if (firstErr && typeof firstErr.msg === "string") {
        const field = Array.isArray(firstErr.loc)
          ? firstErr.loc.slice(1).join(".")
          : ""
        return field ? `${field}: ${firstErr.msg}` : firstErr.msg
      }
    }

    // 4. { message: "string" }
    if (typeof errorObj.message === "string") {
      return errorObj.message
    }
  }

  // Fallbacks by HTTP status code
  switch (status) {
    case 400:
      return "Bad request. Please verify the submitted data."
    case 401:
      return "Authentication required. Please sign in to continue."
    case 403:
      return "You do not have permission to perform this action."
    case 404:
      return "Requested resource was not found."
    case 422:
      return "Validation error. Please check your form input values."
    case 500:
      return "Internal server error. Please try again later."
    case 503:
      return "Service temporarily unavailable. Please verify backend connectivity."
    default:
      return `Request failed with status ${status}.`
  }
}

/**
 * Generic typed HTTP request function.
 */
export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { body, params, headers: customHeaders, ...restOptions } = options

  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`
  const queryString = buildQueryString(params)
  const url = `${API_BASE_URL}${cleanEndpoint}${queryString}`

  const headers = new Headers(customHeaders || {})

  // Attach Supabase access token if available
  const token = await getAccessToken()
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  if (body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json")
  }

  const fetchOptions: RequestInit = {
    ...restOptions,
    headers,
  }

  if (body !== undefined) {
    fetchOptions.body = JSON.stringify(body)
  }

  let response: Response
  try {
    response = await fetch(url, fetchOptions)
  } catch (err: unknown) {
    const errorMsg =
      err instanceof Error && err.name === "AbortError"
        ? "Request was cancelled."
        : "Unable to connect to the backend server. Please verify the service is running."
    throw new ApiClientError(errorMsg, 0, err)
  }

  // Handle empty responses (204 No Content or zero-length bodies)
  if (response.status === 204) {
    return {} as T
  }

  const contentLength = response.headers.get("content-length")
  if (contentLength === "0") {
    return {} as T
  }

  let data: unknown
  const contentType = response.headers.get("content-type") || ""
  if (contentType.includes("application/json")) {
    try {
      data = await response.json()
    } catch {
      data = null
    }
  } else {
    data = await response.text()
  }

  if (!response.ok) {
    const message = extractErrorMessage(response.status, data)
    throw new ApiClientError(message, response.status, data)
  }

  return data as T
}

// Convenience methods
apiClient.get = <T>(endpoint: string, options?: Omit<RequestOptions, "method">) =>
  apiClient<T>(endpoint, { ...options, method: "GET" })

apiClient.post = <T>(
  endpoint: string,
  body?: unknown,
  options?: Omit<RequestOptions, "method" | "body">
) => apiClient<T>(endpoint, { ...options, method: "POST", body })

apiClient.patch = <T>(
  endpoint: string,
  body?: unknown,
  options?: Omit<RequestOptions, "method" | "body">
) => apiClient<T>(endpoint, { ...options, method: "PATCH", body })

apiClient.put = <T>(
  endpoint: string,
  body?: unknown,
  options?: Omit<RequestOptions, "method" | "body">
) => apiClient<T>(endpoint, { ...options, method: "PUT", body })

apiClient.delete = <T>(
  endpoint: string,
  options?: Omit<RequestOptions, "method">
) => apiClient<T>(endpoint, { ...options, method: "DELETE" })
