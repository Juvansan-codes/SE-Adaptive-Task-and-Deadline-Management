/**
 * Core type definitions for Adaptive Task & Deadline Management
 */

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

export * from "./auth";
export * from "./task";
export * from "./dashboard";
export * from "./schedule";
