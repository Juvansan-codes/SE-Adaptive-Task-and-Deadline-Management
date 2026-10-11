import { Button } from "@/components/ui/button";
import { CheckCircle2 } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 text-center">
      <div className="flex flex-col items-center gap-4 max-w-md p-6 rounded-xl border bg-card text-card-foreground shadow-sm">
        <CheckCircle2 className="h-10 w-10 text-emerald-500" />
        <h1 className="text-2xl font-bold tracking-tight">
          Adaptive Task &amp; Deadline Management
        </h1>
        <p className="text-sm text-muted-foreground">
          Phase 0: Project foundation initialized successfully.
        </p>
        <Button variant="outline" size="sm" className="mt-2">
          Foundation Verified
        </Button>
      </div>
    </main>
  );
}
