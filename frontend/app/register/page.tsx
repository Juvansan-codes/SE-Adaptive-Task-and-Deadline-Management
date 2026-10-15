"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { toast } from "sonner"
import { AlertCircle, Loader2, Sparkles } from "lucide-react"

import { registerSchema, type RegisterFormData } from "@/lib/validations/auth"
import { authService } from "@/services/api/auth"
import { AuthCard } from "@/components/auth/auth-card"
import { PasswordInput } from "@/components/auth/password-input"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function RegisterPage() {
  const router = useRouter()
  const [formError, setFormError] = React.useState<string | null>(null)

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  })

  const onSubmit = async (data: RegisterFormData) => {
    setFormError(null)
    try {
      const result = await authService.register(data)

      if (!result.success) {
        setFormError(result.error)
        if (result.fieldErrors?.email) {
          setError("email", { message: result.fieldErrors.email })
        }
        toast.error("Registration was not completed.")
        return
      }

      toast.success(result.message || "Account created successfully!")
      router.push("/dashboard")
    } catch {
      setFormError("An unexpected error occurred during registration.")
      toast.error("Registration failed.")
    }
  }

  // Pre-fill demo data for rapid manual testing
  const handleFillDemo = () => {
    const randomId = Math.floor(Math.random() * 1000)
    setValue("name", "Alex Developer", { shouldValidate: true })
    setValue("email", `developer${randomId}@example.com`, { shouldValidate: true })
    setValue("password", "SecurePassword123!", { shouldValidate: true })
    setValue("confirmPassword", "SecurePassword123!", { shouldValidate: true })
    setFormError(null)
  }

  return (
    <AuthCard
      title="Create an account"
      subtitle="Start managing adaptive tasks and flexible deadlines"
      footerPrompt="Already have an account?"
      footerLinkText="Sign in"
      footerLinkHref="/login"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {/* Form-level error alert */}
        {formError && (
          <div
            role="alert"
            className="flex items-start gap-2.5 rounded-md border border-destructive/20 bg-destructive/10 p-3 text-xs text-destructive transition-colors"
          >
            <AlertCircle className="size-4 shrink-0 mt-0.5" aria-hidden="true" />
            <div className="flex-1 font-medium">{formError}</div>
          </div>
        )}

        {/* Full Name field */}
        <div className="space-y-1.5">
          <label
            htmlFor="name"
            className="text-xs font-medium text-foreground"
          >
            Full name
          </label>
          <Input
            id="name"
            type="text"
            autoComplete="name"
            placeholder="Alex Developer"
            disabled={isSubmitting}
            aria-invalid={!!errors.name}
            aria-describedby={errors.name ? "name-error" : undefined}
            {...register("name")}
          />
          {errors.name && (
            <p
              id="name-error"
              className="text-xs font-medium text-destructive"
              role="alert"
            >
              {errors.name.message}
            </p>
          )}
        </div>

        {/* Email field */}
        <div className="space-y-1.5">
          <label
            htmlFor="email"
            className="text-xs font-medium text-foreground"
          >
            Work email
          </label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="alex@example.com"
            disabled={isSubmitting}
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? "email-error" : undefined}
            {...register("email")}
          />
          {errors.email && (
            <p
              id="email-error"
              className="text-xs font-medium text-destructive"
              role="alert"
            >
              {errors.email.message}
            </p>
          )}
        </div>

        {/* Password field */}
        <div className="space-y-1.5">
          <label
            htmlFor="password"
            className="text-xs font-medium text-foreground"
          >
            Password
          </label>
          <PasswordInput
            id="password"
            autoComplete="new-password"
            placeholder="Minimum 8 characters"
            disabled={isSubmitting}
            aria-invalid={!!errors.password}
            aria-describedby={errors.password ? "password-error" : undefined}
            {...register("password")}
          />
          {errors.password && (
            <p
              id="password-error"
              className="text-xs font-medium text-destructive"
              role="alert"
            >
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Confirm Password field */}
        <div className="space-y-1.5">
          <label
            htmlFor="confirmPassword"
            className="text-xs font-medium text-foreground"
          >
            Confirm password
          </label>
          <PasswordInput
            id="confirmPassword"
            autoComplete="new-password"
            placeholder="Re-enter your password"
            disabled={isSubmitting}
            aria-invalid={!!errors.confirmPassword}
            aria-describedby={errors.confirmPassword ? "confirmPassword-error" : undefined}
            {...register("confirmPassword")}
          />
          {errors.confirmPassword && (
            <p
              id="confirmPassword-error"
              className="text-xs font-medium text-destructive"
              role="alert"
            >
              {errors.confirmPassword.message}
            </p>
          )}
        </div>

        {/* Submit button */}
        <Button
          type="submit"
          variant="primary"
          className="w-full mt-2"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="size-4 animate-spin motion-reduce:animate-none" />
              <span>Creating account...</span>
            </>
          ) : (
            <span>Create account</span>
          )}
        </Button>

        {/* Quick demo fill button */}
        <div className="pt-2 text-center">
          <button
            type="button"
            onClick={handleFillDemo}
            className="inline-flex items-center gap-1.5 text-[11px] text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          >
            <Sparkles className="size-3 text-primary" />
            <span>Generate demo registration data</span>
          </button>
        </div>
      </form>
    </AuthCard>
  )
}
