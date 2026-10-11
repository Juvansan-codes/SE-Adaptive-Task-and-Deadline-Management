/**
 * API configuration module
 * Centralizes the base URL configuration for future API integrations.
 */
export const API_BASE_URL: string =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
