import { Button as ButtonPrimitive } from "@base-ui/react/button"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "cn"

const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center rounded-[6px] border border-transparent bg-clip-padding text-[13px] font-medium whitespace-nowrap transition-colors outline-none select-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/40 focus-visible:ring-offset-1 active:translate-y-[0.5px] disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-2 aria-invalid:ring-destructive/20 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        primary: "bg-primary text-primary-foreground hover:bg-brand-orange-hover shadow-[0_1px_2px_rgba(0,0,0,0.03)]",
        default: "bg-primary text-primary-foreground hover:bg-brand-orange-hover shadow-[0_1px_2px_rgba(0,0,0,0.03)]",
        outline:
          "border-border bg-background hover:bg-muted hover:text-foreground shadow-[0_1px_2px_rgba(0,0,0,0.03)]",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-neutral-200/70 dark:hover:bg-neutral-800",
        ghost:
          "hover:bg-muted hover:text-foreground",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-[0_1px_2px_rgba(0,0,0,0.03)]",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-3 py-1.5 gap-2 text-[13px]",
        sm: "h-8 px-2.5 py-1 gap-1.5 text-xs rounded-[6px]",
        lg: "h-10 px-4 py-2 gap-2 text-sm rounded-[6px]",
        icon: "size-9 rounded-[6px]",
        "icon-sm": "size-8 rounded-[6px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonPrimitive.Props & VariantProps<typeof buttonVariants>) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
