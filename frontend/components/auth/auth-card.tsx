import * as React from "react"
import Link from "next/link"
import { Clock, Info } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface AuthCardProps {
  title: string
  subtitle: string
  children: React.ReactNode
  footerPrompt: string
  footerLinkText: string
  footerLinkHref: string
}

export function AuthCard({
  title,
  subtitle,
  children,
  footerPrompt,
  footerLinkText,
  footerLinkHref,
}: AuthCardProps) {
  return (
    <div className="flex min-h-screen w-full flex-col justify-center py-10 px-4 sm:px-6 lg:px-8 bg-background">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center">
          <Link
            href="/dashboard"
            className="flex items-center gap-2.5 rounded-md p-1.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40"
            aria-label="Adaptive Tasks Homepage"
          >
            <div className="flex size-9 items-center justify-center rounded-md bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 shadow-2xs">
              <Clock className="size-4 text-primary" />
            </div>
            <span className="text-base font-semibold tracking-tight text-foreground">
              Adaptive Tasks
            </span>
          </Link>
          <h1 className="mt-5 text-xl font-semibold tracking-tight text-foreground sm:text-2xl">
            {title}
          </h1>
          <p className="mt-1.5 text-xs text-muted-foreground sm:text-sm">
            {subtitle}
          </p>
        </div>

        {/* Auth Form Card */}
        <div className="mt-6 rounded-lg border border-border bg-card p-6 shadow-2xs sm:p-8">
          {children}

          {/* Footer Navigation Link */}
          <div className="mt-6 border-t border-border pt-4 text-center text-xs text-muted-foreground">
            <span>{footerPrompt} </span>
            <Link
              href={footerLinkHref}
              className="font-medium text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40 rounded px-1 py-0.5"
            >
              {footerLinkText}
            </Link>
          </div>
        </div>

        {/* Prototype Security Notice */}
        <div className="mt-5 flex items-center justify-center gap-2 text-center">
          <Badge
            variant="outline"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-normal text-muted-foreground border-border bg-secondary/40"
          >
            <Info className="size-3 text-muted-foreground" />
            <span>Prototype: Authentication is mocked for UI testing</span>
          </Badge>
        </div>
      </div>
    </div>
  )
}
