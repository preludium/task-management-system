import type { VariantProps } from "class-variance-authority"
import { cva } from "class-variance-authority"

export { default as Button } from "./Button.vue"

export const buttonVariants = cva(
  [
    // Base Layout & Typography
    'inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium',

    // Spacing & Border
    'rounded-md',

    // Colors & States
    'transition-all',

    // Focus & Interaction
    'outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] enabled:hover:cursor-pointer',

    // Disabled State
    'disabled:pointer-events-none disabled:opacity-50',

    // Validation States
    'aria-invalid:ring-destructive/20 aria-invalid:border-destructive',

    // Icon Styling
    '[&_svg]:pointer-events-none [&_svg:not([class*=\'size-\'])]:size-4 shrink-0 [&_svg]:shrink-0',
  ].join(' '),
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90",
        destructive:
          "bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20",
        outline:
          "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80",
        ghost:
          "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
)

export type ButtonVariants = VariantProps<typeof buttonVariants>
