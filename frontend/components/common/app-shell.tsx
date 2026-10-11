"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  CheckSquare,
  Calendar,
  Settings,
  Menu,
  X,
  Clock,
  Sparkles,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface NavItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  badge?: string
}

const mainNavItems: NavItem[] = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Tasks", href: "/tasks", icon: CheckSquare },
  { name: "Schedule", href: "/schedule", icon: Calendar },
]

const secondaryNavItems: NavItem[] = [
  { name: "Settings", href: "/settings", icon: Settings },
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false)

  // Close mobile menu on Escape key
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && mobileMenuOpen) {
        setMobileMenuOpen(false)
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [mobileMenuOpen])

  // Prevent background scroll when mobile drawer is open
  React.useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = ""
    }
    return () => {
      document.body.style.overflow = ""
    }
  }, [mobileMenuOpen])

  // Helper to determine if link is active
  const isLinkActive = React.useCallback(
    (href: string) => {
      if (href === "/dashboard") {
        return pathname === "/dashboard" || pathname === "/"
      }
      return pathname.startsWith(href)
    },
    [pathname]
  )

  // Get current page title for top bar
  const currentPageTitle = React.useMemo(() => {
    const allItems = [...mainNavItems, ...secondaryNavItems]
    const matched = allItems.find((item) => isLinkActive(item.href))
    return matched ? matched.name : "Workspace"
  }, [isLinkActive])

  // If on authentication route, render without dashboard shell
  const isAuthRoute = pathname === "/login" || pathname === "/register"
  if (isAuthRoute) {
    return (
      <div className="min-h-screen w-full bg-background text-foreground flex flex-col">
        {children}
      </div>
    )
  }

  return (
    <div className="flex min-h-screen w-full bg-background text-foreground">
      {/* Accessibility Skip Link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground focus:shadow-md"
      >
        Skip to main content
      </a>

      {/* DESKTOP SIDEBAR */}
      <aside
        className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 z-30 border-r border-border bg-sidebar"
        aria-label="Desktop Sidebar Navigation"
      >
        {/* Brand Area */}
        <div className="flex h-16 items-center gap-2.5 px-5 border-b border-sidebar-border">
          <div className="flex size-8 items-center justify-center rounded-md bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 shadow-2xs">
            <Clock className="size-4 text-primary" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold tracking-tight text-foreground">
              Adaptive Tasks
            </span>
            <span className="text-[11px] font-medium text-muted-foreground">
              Adaptive Scheduling
            </span>
          </div>
        </div>

        {/* Navigation Area */}
        <div className="flex flex-1 flex-col justify-between p-3.5 overflow-y-auto">
          {/* Main Links */}
          <nav className="flex flex-col gap-1" aria-label="Main Navigation">
            <div className="px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
              Overview
            </div>
            {mainNavItems.map((item) => {
              const active = isLinkActive(item.href)
              const Icon = item.icon
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "group flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring/40",
                    active
                      ? "bg-accent text-accent-foreground font-semibold border-l-2 border-primary"
                      : "text-muted-foreground hover:bg-neutral-100 hover:text-foreground dark:hover:bg-neutral-800/60"
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon
                      className={cn(
                        "size-4 shrink-0 transition-colors",
                        active ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                      )}
                    />
                    <span>{item.name}</span>
                  </div>
                  {active && (
                    <span className="size-1.5 rounded-full bg-primary" />
                  )}
                </Link>
              )
            })}
          </nav>

          {/* Bottom Settings & Status */}
          <div className="flex flex-col gap-3 pt-4 border-t border-sidebar-border">
            <nav className="flex flex-col gap-1" aria-label="Secondary Navigation">
              {secondaryNavItems.map((item) => {
                const active = isLinkActive(item.href)
                const Icon = item.icon
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    aria-current={active ? "page" : undefined}
                    className={cn(
                      "group flex items-center justify-between rounded-md px-3 py-2 text-sm font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring/40",
                      active
                        ? "bg-accent text-accent-foreground font-semibold border-l-2 border-primary"
                        : "text-muted-foreground hover:bg-neutral-100 hover:text-foreground dark:hover:bg-neutral-800/60"
                    )}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon
                        className={cn(
                          "size-4 shrink-0 transition-colors",
                          active ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                        )}
                      />
                      <span>{item.name}</span>
                    </div>
                  </Link>
                )
              })}
            </nav>

            {/* System Status Pill */}
            <div className="flex items-center justify-between rounded-md border border-border bg-background px-3 py-2 text-xs">
              <div className="flex items-center gap-2">
                <span className="size-2 rounded-full bg-primary" />
                <span className="font-medium text-foreground">Phase 1</span>
              </div>
              <Badge variant="outline" className="text-[10px] py-0 px-1.5 font-normal">
                Active
              </Badge>
            </div>
          </div>
        </div>
      </aside>

      {/* MOBILE DRAWER OVERLAY */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-xs md:hidden"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* MOBILE DRAWER */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-sidebar border-r border-sidebar-border transition-transform duration-200 ease-in-out md:hidden",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        )}
        role="dialog"
        aria-modal="true"
        aria-label="Mobile Navigation"
      >
        <div className="flex h-16 items-center justify-between px-5 border-b border-sidebar-border">
          <div className="flex items-center gap-2.5">
            <div className="flex size-8 items-center justify-center rounded-md bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900">
              <Clock className="size-4 text-primary" />
            </div>
            <span className="text-sm font-semibold tracking-tight text-foreground">
              Adaptive Tasks
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close navigation menu"
          >
            <X className="size-4" />
          </Button>
        </div>

        <div className="flex flex-1 flex-col justify-between p-4 overflow-y-auto">
          <nav className="flex flex-col gap-1.5" aria-label="Mobile Main Navigation">
            <div className="px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
              Overview
            </div>
            {mainNavItems.map((item) => {
              const active = isLinkActive(item.href)
              const Icon = item.icon
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "flex items-center justify-between rounded-md px-3.5 py-2.5 text-sm font-medium transition-colors min-h-[44px]",
                    active
                      ? "bg-accent text-accent-foreground font-semibold border-l-2 border-primary"
                      : "text-muted-foreground hover:bg-neutral-100 hover:text-foreground dark:hover:bg-neutral-800/60"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={cn("size-4", active ? "text-primary" : "text-muted-foreground")} />
                    <span>{item.name}</span>
                  </div>
                  {active && <span className="size-1.5 rounded-full bg-primary" />}
                </Link>
              )
            })}
          </nav>

          <div className="flex flex-col gap-3 pt-4 border-t border-sidebar-border">
            <nav className="flex flex-col gap-1.5" aria-label="Mobile Secondary Navigation">
              {secondaryNavItems.map((item) => {
                const active = isLinkActive(item.href)
                const Icon = item.icon
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    aria-current={active ? "page" : undefined}
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      "flex items-center justify-between rounded-md px-3.5 py-2.5 text-sm font-medium transition-colors min-h-[44px]",
                      active
                        ? "bg-accent text-accent-foreground font-semibold border-l-2 border-primary"
                        : "text-muted-foreground hover:bg-neutral-100 hover:text-foreground dark:hover:bg-neutral-800/60"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={cn("size-4", active ? "text-primary" : "text-muted-foreground")} />
                      <span>{item.name}</span>
                    </div>
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* MAIN LAYOUT AREA */}
      <div className="flex flex-1 flex-col md:pl-64 min-w-0">
        {/* TOP BAR */}
        <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center justify-between border-b border-border bg-background/95 px-4 md:px-8 backdrop-blur-xs">
          <div className="flex items-center gap-3">
            {/* Mobile Hamburger Button */}
            <Button
              variant="outline"
              size="icon-sm"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open navigation menu"
              aria-expanded={mobileMenuOpen}
            >
              <Menu className="size-4" />
            </Button>

            {/* Breadcrumb / Title */}
            <div className="flex items-center gap-2">
              <span className="hidden sm:inline-block text-xs text-muted-foreground">
                Adaptive Task &amp; Deadline Management
              </span>
              <span className="hidden sm:inline-block text-xs text-muted-foreground">/</span>
              <span className="text-sm font-semibold tracking-tight text-foreground">
                {currentPageTitle}
              </span>
            </div>
          </div>

          {/* Right Header Area */}
          <div className="flex items-center gap-2.5">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="text-xs">
                Sign in
              </Button>
            </Link>
            <Badge
              variant="outline"
              className="hidden sm:flex items-center gap-1.5 py-1 text-xs font-normal border-border bg-background"
            >
              <Sparkles className="size-3 text-primary" />
              <span>Shell Active</span>
            </Badge>
            <div className="size-2 rounded-full bg-emerald-500" title="System operational" />
          </div>
        </header>

        {/* PAGE CONTENT CONTAINER */}
        <main id="main-content" className="flex-1 overflow-x-hidden">
          <div className="mx-auto w-full max-w-6xl p-5 md:p-8 lg:p-10">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
