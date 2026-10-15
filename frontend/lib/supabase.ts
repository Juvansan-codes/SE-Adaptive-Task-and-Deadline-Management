import { createClient, SupabaseClient } from "@supabase/supabase-js"

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ""
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ""

export const supabase: SupabaseClient = createClient(
  supabaseUrl || "https://placeholder.supabase.co",
  supabaseAnonKey || "placeholder-anon-key",
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  }
)

/**
 * Retrieve current active Supabase access token for API requests.
 */
export async function getAccessToken(): Promise<string | null> {
  try {
    const {
      data: { session },
      error,
    } = await supabase.auth.getSession()

    if (error || !session) {
      return null
    }

    return session.access_token
  } catch {
    return null
  }
}
