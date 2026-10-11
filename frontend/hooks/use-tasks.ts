import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { mockTaskService } from "@/services/mock/tasks"
import type {
  TaskFilterOptions,
  CreateTaskInput,
  UpdateTaskInput,
  TaskStatus,
} from "@/types/task"

export const TASK_KEYS = {
  all: ["tasks"] as const,
  list: (filter?: TaskFilterOptions) => ["tasks", "list", filter] as const,
  detail: (id: string) => ["tasks", "detail", id] as const,
  categories: ["tasks", "categories"] as const,
}

export function useTasks(filter?: TaskFilterOptions) {
  return useQuery({
    queryKey: TASK_KEYS.list(filter),
    queryFn: () => mockTaskService.getTasks(filter),
  })
}

export function useTask(id: string) {
  return useQuery({
    queryKey: TASK_KEYS.detail(id),
    queryFn: () => mockTaskService.getTask(id),
    enabled: !!id,
  })
}

export function useCategories() {
  return useQuery({
    queryKey: TASK_KEYS.categories,
    queryFn: () => mockTaskService.getCategories(),
  })
}

export function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: CreateTaskInput) => mockTaskService.createTask(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
    },
  })
}

export function useUpdateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: UpdateTaskInput }) =>
      mockTaskService.updateTask(id, updates),
    onSuccess: (updatedTask, variables) => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
      if (variables.id) {
        queryClient.invalidateQueries({ queryKey: TASK_KEYS.detail(variables.id) })
      }
    },
  })
}

export function useDeleteTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => mockTaskService.deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
    },
  })
}

export function useUpdateTaskStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: TaskStatus }) =>
      mockTaskService.updateTask(id, { status }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.detail(variables.id) })
    },
  })
}
