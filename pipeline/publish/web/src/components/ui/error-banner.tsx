import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

/** The boxed destructive error message repeated across the data pages. */
export function ErrorBanner({
  className,
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      className={cn(
        "rounded border border-destructive bg-destructive/5 px-4 py-3 text-sm text-destructive",
        className,
      )}
    >
      {children}
    </div>
  );
}
