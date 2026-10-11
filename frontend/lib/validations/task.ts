import { z } from "zod"

export const taskFormSchema = z.object({
  title: z
    .string()
    .trim()
    .min(1, "Task title is required.")
    .max(120, "Title must be 120 characters or fewer."),
  description: z
    .string()
    .trim()
    .max(1000, "Description must be 1,000 characters or fewer."),
  category: z
    .string()
    .trim()
    .min(1, "Category is required.")
    .max(50, "Category must be 50 characters or fewer."),
  deadline: z
    .string()
    .min(1, "Deadline date is required."),
  priority: z.enum(["low", "medium", "high", "critical"], {
    required_error: "Priority is required.",
  }),
  difficulty: z.enum(["easy", "medium", "hard"], {
    required_error: "Difficulty is required.",
  }),
  estimatedDuration: z.coerce
    .number({ invalid_type_error: "Estimated duration must be a number." })
    .positive("Estimated duration must be greater than 0.")
    .max(500, "Estimated duration cannot exceed 500 hours."),
  completedDuration: z.coerce
    .number({ invalid_type_error: "Completed duration must be a number." })
    .min(0, "Completed duration cannot be negative."),
  status: z.enum(["pending", "in_progress", "completed", "overdue"]),
})

export type TaskFormData = z.infer<typeof taskFormSchema>
