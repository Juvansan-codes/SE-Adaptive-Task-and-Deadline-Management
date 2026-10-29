import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { taskService } from "@/services/api/tasks"
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
    queryFn: () => taskService.getTasks(filter),
  })
}

export function useTask(id: string) {
  return useQuery({
    queryKey: TASK_KEYS.detail(id),
    queryFn: () => taskService.getTask(id),
    enabled: !!id,
  })
}

export function useCategories() {
  return useQuery({
    queryKey: TASK_KEYS.categories,
    queryFn: () => taskService.getCategories(),
  })
}

export function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: CreateTaskInput) => taskService.createTask(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      queryClient.invalidateQueries({ queryKey: ["schedule"] })
    },
  })
}

export function useUpdateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: UpdateTaskInput }) =>
      taskService.updateTask(id, updates),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      queryClient.invalidateQueries({ queryKey: ["schedule"] })
      if (variables.id) {
        queryClient.invalidateQueries({ queryKey: TASK_KEYS.detail(variables.id) })
      }
    },
  })
}

export function useDeleteTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => taskService.deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      queryClient.invalidateQueries({ queryKey: ["schedule"] })
    },
  })
}

export function useUpdateTaskStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: TaskStatus }) =>
      taskService.updateTask(id, { status }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      queryClient.invalidateQueries({ queryKey: ["schedule"] })
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.detail(variables.id) })
    },
  })
}

export function useSeedTasks() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => taskService.seedStarterTasks(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TASK_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      queryClient.invalidateQueries({ queryKey: ["schedule"] })
    },
  })
}
