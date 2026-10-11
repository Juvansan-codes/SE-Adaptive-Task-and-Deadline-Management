import * as React from "react"
import { Suspense } from "react"
import { TaskDetails } from "@/components/tasks/task-details"
import { LoadingState } from "@/components/common/loading-state"

interface TaskDetailsPageProps {
  params: Promise<{ id: string }>
}

async function TaskDetailsContent({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <TaskDetails taskId={id} />
}

export default function TaskDetailsPage({ params }: TaskDetailsPageProps) {
  return (
    <Suspense fallback={<LoadingState message="Loading task details..." />}>
      <TaskDetailsContent params={params} />
    </Suspense>
  )
}
